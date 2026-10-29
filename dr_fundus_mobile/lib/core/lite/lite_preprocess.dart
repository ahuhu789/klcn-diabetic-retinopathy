// Lite (on-device student) preprocessing: a Dart port of dr-fundus-app/backend/app/preprocess.py
// (Ben Graham 512 training-cache recipe) + torchvision Resize((448,448)) + ImageNet normalisation.
// Same algorithm as the web port (frontend/src/lite/preprocess.js), which is bit-exact with
// OpenCV/PIL for images <= 2000 px (checked in dr-fundus-app/lite_parity).
import 'dart:math' as math;
import 'dart:typed_data';

import 'package:image/image.dart' as img;

class RgbImage {
  final Uint8List data; // RGB, row major
  final int width;
  final int height;
  RgbImage(this.data, this.width, this.height);

  factory RgbImage.fromImage(img.Image src) {
    final w = src.width, h = src.height;
    final out = Uint8List(w * h * 3);
    var o = 0;
    for (var y = 0; y < h; y++) {
      for (var x = 0; x < w; x++) {
        final p = src.getPixel(x, y);
        out[o++] = p.r.toInt();
        out[o++] = p.g.toInt();
        out[o++] = p.b.toInt();
      }
    }
    return RgbImage(out, w, h);
  }

  img.Image toImage() {
    return img.Image.fromBytes(
        width: width, height: height, bytes: data.buffer, numChannels: 3, order: img.ChannelOrder.rgb);
  }
}

class LitePreprocess {
  static const int cacheSize = 512;
  static const double sigma = 20.0;
  static const int cropTol = 10;
  static const int jpegQuality = 92;
  static const int inputSize = 448;
  static const int gateSize = 224;
  static const List<double> mean = [0.485, 0.456, 0.406];
  static const List<double> std = [0.229, 0.224, 0.225];

  /// Decode file bytes; EXIF orientation is applied like cv2.imdecode.
  static RgbImage? decode(Uint8List bytes) {
    final d = img.decodeImage(bytes);
    if (d == null) return null;
    return RgbImage.fromImage(img.bakeOrientation(d));
  }

  /// OpenCV IMREAD_REDUCED_COLOR_2/4 for long edge > 2000/4000 (box-average approximation).
  static RgbImage reduceLikeCache(RgbImage im) {
    final longEdge = math.max(im.width, im.height);
    final f = longEdge > 4000 ? 4 : (longEdge > 2000 ? 2 : 1);
    if (f == 1) return im;
    var out = _boxReduce(im, f);
    if (math.max(out.width, out.height) > 2000) out = _boxReduce(out, f);
    return out;
  }

  static RgbImage _boxReduce(RgbImage im, int f) {
    final w = (im.width + f - 1) ~/ f, h = (im.height + f - 1) ~/ f;
    final out = Uint8List(w * h * 3);
    for (var y = 0; y < h; y++) {
      for (var x = 0; x < w; x++) {
        var r = 0, g = 0, b = 0, n = 0;
        for (var yy = y * f; yy < math.min(y * f + f, im.height); yy++) {
          for (var xx = x * f; xx < math.min(x * f + f, im.width); xx++) {
            final k = (yy * im.width + xx) * 3;
            r += im.data[k];
            g += im.data[k + 1];
            b += im.data[k + 2];
            n++;
          }
        }
        final o = (y * w + x) * 3;
        out[o] = (r / n).round();
        out[o + 1] = (g / n).round();
        out[o + 2] = (b / n).round();
      }
    }
    return RgbImage(out, w, h);
  }

  /// cv2 RGB2GRAY (fixed point) + crop rows/cols with gray > tol.
  static RgbImage cropFromGray(RgbImage im, {int tol = cropTol}) {
    final d = im.data, w = im.width, h = im.height;
    var rmin = h, rmax = -1, cmin = w, cmax = -1;
    for (var y = 0; y < h; y++) {
      for (var x = 0; x < w; x++) {
        final k = (y * w + x) * 3;
        final gray = (d[k] * 4899 + d[k + 1] * 9617 + d[k + 2] * 1868 + 8192) >> 14;
        if (gray > tol) {
          if (y < rmin) rmin = y;
          if (y > rmax) rmax = y;
          if (x < cmin) cmin = x;
          if (x > cmax) cmax = x;
        }
      }
    }
    if (rmax < 0 || !(rmax > rmin && cmax > cmin)) return im;
    final cw = cmax - cmin + 1, ch = rmax - rmin + 1;
    final out = Uint8List(cw * ch * 3);
    for (var y = 0; y < ch; y++) {
      final src = ((y + rmin) * w + cmin) * 3;
      out.setRange(y * cw * 3, (y + 1) * cw * 3, d, src);
    }
    return RgbImage(out, cw, ch);
  }

  static List<int> _cvCoef(int o, double scale, int n) {
    var f = (o + 0.5) * scale - 0.5;
    var i = f.floor();
    f -= i;
    if (i < 0) {
      i = 0;
      f = 0;
    }
    if (i >= n - 1) {
      i = n - 1;
      f = 0;
    }
    final a1 = (f * 2048).round();
    return [i, math.min(i + 1, n - 1), 2048 - a1, a1];
  }

  /// cv2.resize INTER_LINEAR for uint8 (OpenCV fixed-point path).
  static RgbImage resizeBilinearCv(RgbImage im, int ow, int oh) {
    final d = im.data, iw = im.width, ih = im.height;
    final xs = List.generate(ow, (x) => _cvCoef(x, iw / ow, iw));
    final out = Uint8List(ow * oh * 3);
    for (var y = 0; y < oh; y++) {
      final cy = _cvCoef(y, ih / oh, ih);
      final j0 = cy[0], j1 = cy[1], b0 = cy[2], b1 = cy[3];
      for (var x = 0; x < ow; x++) {
        final cx = xs[x];
        final i0 = cx[0], i1 = cx[1], a0 = cx[2], a1 = cx[3];
        for (var c = 0; c < 3; c++) {
          final s0 = d[(j0 * iw + i0) * 3 + c] * a0 + d[(j0 * iw + i1) * 3 + c] * a1;
          final s1 = d[(j1 * iw + i0) * 3 + c] * a0 + d[(j1 * iw + i1) * 3 + c] * a1;
          final v = ((((s0 >> 4) * b0) >> 16) + (((s1 >> 4) * b1) >> 16) + 2) >> 2;
          out[(y * ow + x) * 3 + c] = v < 0 ? 0 : (v > 255 ? 255 : v);
        }
      }
    }
    return RgbImage(out, ow, oh);
  }

  /// OpenCV bit-exact Gaussian kernel (8 fractional bits, error-diffusion rounding).
  static List<int> gaussianKernelFixed([double s = sigma]) {
    final n = ((s * 3 * 2 + 1).round()) | 1;
    final c = (n - 1) ~/ 2;
    final k = List<double>.generate(n, (i) => math.exp(-((i - c) * (i - c)) / (2 * s * s)));
    final total = k.fold<double>(0, (a, b) => a + b);
    final res = List<int>.filled(n, 0);
    var err = 0.0;
    var sum = 0;
    for (var i = 0; i < c; i++) {
      final adj = (k[i] / total) * 256 + err;
      final v = _roundHalfAwayFromZero(adj);
      err = adj - v;
      res[i] = v;
      res[n - 1 - i] = v;
      sum += v;
    }
    res[c] = 256 - 2 * sum;
    return res;
  }

  // Matches JS Math.round for the non-negative values used here.
  static int _roundHalfAwayFromZero(double v) => (v + 0.5).floor();

  static int _reflect101(int i, int n) {
    while (i < 0 || i >= n) {
      if (i < 0) i = -i;
      if (i >= n) i = 2 * n - 2 - i;
    }
    return i;
  }

  /// cv2.GaussianBlur(img, (0,0), 20) for uint8 (bit-exact path), BORDER_REFLECT_101.
  static Uint8List gaussianBlur(RgbImage im) {
    final d = im.data, w = im.width, h = im.height;
    final k = gaussianKernelFixed();
    final ks = k.length, r = (ks - 1) ~/ 2;
    final taps = <int>[];
    for (var t = 0; t < ks; t++) {
      if (k[t] != 0) taps.add(t);
    }
    final xIdx = List<int>.generate(w + 2 * r, (i) => _reflect101(i - r, w));
    final yIdx = List<int>.generate(h + 2 * r, (i) => _reflect101(i - r, h));
    final tmp = Int32List(w * h * 3);
    for (var y = 0; y < h; y++) {
      for (var x = 0; x < w; x++) {
        var a0 = 0, a1 = 0, a2 = 0;
        for (final t in taps) {
          final q = (y * w + xIdx[x + t]) * 3;
          final kv = k[t];
          a0 += d[q] * kv;
          a1 += d[q + 1] * kv;
          a2 += d[q + 2] * kv;
        }
        final o = (y * w + x) * 3;
        tmp[o] = a0;
        tmp[o + 1] = a1;
        tmp[o + 2] = a2;
      }
    }
    final out = Uint8List(w * h * 3);
    for (var y = 0; y < h; y++) {
      for (var x = 0; x < w; x++) {
        var a0 = 0, a1 = 0, a2 = 0;
        for (final t in taps) {
          final q = (yIdx[y + t] * w + x) * 3;
          final kv = k[t];
          a0 += tmp[q] * kv;
          a1 += tmp[q + 1] * kv;
          a2 += tmp[q + 2] * kv;
        }
        final o = (y * w + x) * 3;
        out[o] = math.min(255, (a0 + 32768) >> 16);
        out[o + 1] = math.min(255, (a1 + 32768) >> 16);
        out[o + 2] = math.min(255, (a2 + 32768) >> 16);
      }
    }
    return out;
  }

  /// ben_graham_uint8: crop -> resize 512 -> 4*img - 4*blur + 128 -> circle mask (r = 0.95*256).
  static RgbImage benGraham(RgbImage im, {int size = cacheSize}) {
    final cropped = cropFromGray(im);
    if (cropped.width < 2 || cropped.height < 2) {
      throw StateError('Ben Graham crop produced an empty image');
    }
    final resized = resizeBilinearCv(cropped, size, size);
    final blur = gaussianBlur(resized);
    final out = Uint8List(size * size * 3);
    final cx = size ~/ 2, cy = size ~/ 2;
    final radius = (math.min(cx, cy) * 0.95).truncate();
    for (var y = 0; y < size; y++) {
      for (var x = 0; x < size; x++) {
        final inside = (x - cx) * (x - cx) + (y - cy) * (y - cy) <= radius * radius;
        for (var c = 0; c < 3; c++) {
          final o = (y * size + x) * 3 + c;
          if (!inside) {
            out[o] = 128;
          } else {
            final v = 4 * resized.data[o] - 4 * blur[o] + 128;
            out[o] = v < 0 ? 0 : (v > 255 ? 255 : v);
          }
        }
      }
    }
    return RgbImage(out, size, size);
  }

  /// JPEG q92 round trip (the training cache was stored as JPEG q92, 4:2:0).
  static RgbImage jpegRoundtrip(RgbImage im) {
    final jpg = img.encodeJpg(im.toImage(), quality: jpegQuality, chroma: img.JpegChroma.yuv420);
    return RgbImage.fromImage(img.decodeJpg(jpg)!);
  }

  /// PIL Image.resize(BILINEAR) with antialias support and 8-bit fixed point (22 bits).
  static RgbImage resizePilBilinear(RgbImage im, int ow, int oh) {
    var cur = im;
    if (ow != cur.width) cur = _pilPass(cur, ow, true);
    if (oh != cur.height) cur = _pilPass(cur, oh, false);
    return cur;
  }

  static RgbImage _pilPass(RgbImage im, int outSize, bool horizontal) {
    final d = im.data, iw = im.width, ih = im.height;
    final inSize = horizontal ? iw : ih;
    final scale = inSize / outSize;
    final filterscale = math.max(scale, 1.0);
    final support = 1.0 * filterscale;
    final bounds = <List<int>>[];
    final kk = <List<int>>[];
    for (var xx = 0; xx < outSize; xx++) {
      final center = (xx + 0.5) * scale;
      final ss = 1.0 / filterscale;
      var xmin = (center - support + 0.5).truncate();
      if (xmin < 0) xmin = 0;
      var xmax = (center + support + 0.5).truncate();
      if (xmax > inSize) xmax = inSize;
      xmax -= xmin;
      final k = List<double>.filled(xmax, 0);
      var ww = 0.0;
      for (var x = 0; x < xmax; x++) {
        var t = (x + xmin - center + 0.5) * ss;
        if (t < 0) t = -t;
        final w = t < 1 ? 1 - t : 0.0;
        k[x] = w;
        ww += w;
      }
      final ik = List<int>.filled(xmax, 0);
      for (var x = 0; x < xmax; x++) {
        final v = ww != 0 ? k[x] / ww : k[x];
        ik[x] = v < 0 ? (-0.5 + v * (1 << 22)).truncate() : (0.5 + v * (1 << 22)).truncate();
      }
      bounds.add([xmin, xmax]);
      kk.add(ik);
    }
    final ow = horizontal ? outSize : iw, oh = horizontal ? ih : outSize;
    final out = Uint8List(ow * oh * 3);
    const half = 1 << 21;
    for (var y = 0; y < oh; y++) {
      for (var x = 0; x < ow; x++) {
        final b = bounds[horizontal ? x : y];
        final k = kk[horizontal ? x : y];
        final mn = b[0], n = b[1];
        for (var c = 0; c < 3; c++) {
          var s = half;
          for (var t = 0; t < n; t++) {
            final q = horizontal ? (y * iw + mn + t) * 3 + c : ((mn + t) * iw + x) * 3 + c;
            s += d[q] * k[t];
          }
          final v = s >> 22;
          out[(y * ow + x) * 3 + c] = v < 0 ? 0 : (v > 255 ? 255 : v);
        }
      }
    }
    return RgbImage(out, ow, oh);
  }

  /// 448 RGB uint8 -> NHWC Float32 ImageNet-normalised (TFLite layout), optional h-flip.
  static Float32List toNhwcNormalized(RgbImage im, {bool flip = false}) {
    final w = im.width, h = im.height;
    final out = Float32List(w * h * 3);
    for (var y = 0; y < h; y++) {
      for (var x = 0; x < w; x++) {
        final sx = flip ? w - 1 - x : x;
        final q = (y * w + sx) * 3;
        final o = (y * w + x) * 3;
        for (var c = 0; c < 3; c++) {
          out[o + c] = (im.data[q + c] / 255.0 - mean[c]) / std[c];
        }
      }
    }
    return out;
  }

  /// Full student pipeline: returns [input, flipped input] (NHWC) and the 512 cache image.
  static ({Float32List input, Float32List flipped, RgbImage cache512}) studentInputs(RgbImage im) {
    final bg = benGraham(reduceLikeCache(im));
    final cache512 = jpegRoundtrip(bg);
    final x448 = resizePilBilinear(cache512, inputSize, inputSize);
    return (
      input: toNhwcNormalized(x448),
      flipped: toNhwcNormalized(x448, flip: true),
      cache512: cache512,
    );
  }
}

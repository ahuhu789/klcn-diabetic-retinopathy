// Lite (on-device student) preprocessing, a pure-JS port of backend/app/preprocess.py
// (Ben Graham 512 cache recipe) + torchvision Resize((448,448)) + ImageNet normalisation.
// Everything works on plain RGB Uint8Arrays so the same code runs in the browser and in
// node (lite_parity/). The JPEG q92 round trip is injected because it is platform specific.

export const CACHE_SIZE = 512;
export const SIGMA_X = 20;
export const CROP_TOL = 10;
export const JPEG_QUALITY = 0.92;
export const INPUT_SIZE = 448;
export const GATE_SIZE = 224;
const MEAN = [0.485, 0.456, 0.406];
const STD = [0.229, 0.224, 0.225];

/** RGBA (canvas ImageData) -> {data: RGB Uint8Array, width, height} */
export function rgbaToRgb(rgba, width, height) {
  const out = new Uint8Array(width * height * 3);
  for (let i = 0, j = 0; i < width * height; i++, j += 4) {
    out[i * 3] = rgba[j]; out[i * 3 + 1] = rgba[j + 1]; out[i * 3 + 2] = rgba[j + 2];
  }
  return { data: out, width, height };
}

/** Step 1 of decode_like_cache: OpenCV IMREAD_REDUCED_COLOR_2/4 for long edge > 2000/4000.
 * libjpeg DCT scaling is approximated by a box average over factor x factor blocks. */
export function reduceLikeCache(img) {
  const longEdge = Math.max(img.width, img.height);
  const factor = longEdge > 4000 ? 4 : longEdge > 2000 ? 2 : 1;
  if (factor === 1) return img;
  let out = boxReduce(img, factor);
  if (Math.max(out.width, out.height) > 2000) out = boxReduce(out, factor);
  return out;
}

function boxReduce(img, f) {
  const w = Math.ceil(img.width / f), h = Math.ceil(img.height / f);
  const out = new Uint8Array(w * h * 3);
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      let r = 0, g = 0, b = 0, n = 0;
      for (let yy = y * f; yy < Math.min(y * f + f, img.height); yy++) {
        for (let xx = x * f; xx < Math.min(x * f + f, img.width); xx++) {
          const k = (yy * img.width + xx) * 3;
          r += img.data[k]; g += img.data[k + 1]; b += img.data[k + 2]; n++;
        }
      }
      const o = (y * w + x) * 3;
      out[o] = Math.round(r / n); out[o + 1] = Math.round(g / n); out[o + 2] = Math.round(b / n);
    }
  }
  return { data: out, width: w, height: h };
}

/** cv2.cvtColor RGB2GRAY (fixed point) and crop rows/cols with gray > tol. */
export function cropImageFromGray(img, tol = CROP_TOL) {
  const { data, width, height } = img;
  let rmin = height, rmax = -1, cmin = width, cmax = -1;
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const k = (y * width + x) * 3;
      const gray = (data[k] * 4899 + data[k + 1] * 9617 + data[k + 2] * 1868 + 8192) >> 14;
      if (gray > tol) {
        if (y < rmin) rmin = y; if (y > rmax) rmax = y;
        if (x < cmin) cmin = x; if (x > cmax) cmax = x;
      }
    }
  }
  if (rmax < 0) return img;
  if (!(rmax > rmin && cmax > cmin)) return img;
  const w = cmax - cmin + 1, h = rmax - rmin + 1;
  const out = new Uint8Array(w * h * 3);
  for (let y = 0; y < h; y++) {
    const src = ((y + rmin) * width + cmin) * 3;
    out.set(data.subarray(src, src + w * 3), y * w * 3);
  }
  return { data: out, width: w, height: h };
}

/** cv2.resize INTER_LINEAR for uint8 (half-pixel centres, no antialias), matching OpenCV's
 * fixed-point path: 11-bit coefficients, horizontal int sums, vertical
 * ((S0>>4)*b0 >> 16) + ((S1>>4)*b1 >> 16) + 2 >> 2 (VResizeLinearVec_32s8u). */
export function resizeBilinearCv(img, ow, oh) {
  const { data, width: iw, height: ih } = img;
  const coef = (o, scale, n) => {
    let f = (o + 0.5) * scale - 0.5; let i = Math.floor(f); f -= i;
    if (i < 0) { i = 0; f = 0; }
    if (i >= n - 1) { i = n - 1; f = 0; }
    const a1 = Math.round(f * 2048);
    return [i, Math.min(i + 1, n - 1), 2048 - a1, a1];
  };
  const xs = []; for (let x = 0; x < ow; x++) xs.push(coef(x, iw / ow, iw));
  const out = new Uint8Array(ow * oh * 3);
  for (let y = 0; y < oh; y++) {
    const [j0, j1, b0, b1] = coef(y, ih / oh, ih);
    for (let x = 0; x < ow; x++) {
      const [i0, i1, a0, a1] = xs[x];
      for (let c = 0; c < 3; c++) {
        const s0 = data[(j0 * iw + i0) * 3 + c] * a0 + data[(j0 * iw + i1) * 3 + c] * a1;
        const s1 = data[(j1 * iw + i0) * 3 + c] * a0 + data[(j1 * iw + i1) * 3 + c] * a1;
        const v = ((((s0 >> 4) * b0) >> 16) + (((s1 >> 4) * b1) >> 16) + 2) >> 2;
        out[(y * ow + x) * 3 + c] = v < 0 ? 0 : v > 255 ? 255 : v;
      }
    }
  }
  return { data: out, width: ow, height: oh };
}

/** OpenCV fixed-point (bit-exact) Gaussian kernel: ksize = round(sigma*6+1)|1, values with
 * 8 fractional bits, rounded with error diffusion (getGaussianKernelFixedPoint_ED). */
export function gaussianKernelFixed(sigma = SIGMA_X) {
  const n = (Math.round(sigma * 3 * 2 + 1)) | 1; const c = (n - 1) / 2;
  const k = new Float64Array(n); let s = 0;
  for (let i = 0; i < n; i++) { k[i] = Math.exp(-((i - c) ** 2) / (2 * sigma * sigma)); s += k[i]; }
  const res = new Int32Array(n); let err = 0, sum = 0;
  for (let i = 0; i < c; i++) {
    const adj = (k[i] / s) * 256 + err; const v = Math.round(adj); err = adj - v;
    res[i] = v; res[n - 1 - i] = v; sum += v;
  }
  res[c] = 256 - 2 * sum;
  return res;
}

/** cv2.GaussianBlur(img, (0,0), sigma) for uint8 (bit-exact path), BORDER_REFLECT_101.
 * Row pass sums k*p exactly, column pass sums k*row, output = (sum + 2^15) >> 16. */
export function gaussianBlur(img, sigma = SIGMA_X) {
  const { data, width: w, height: h } = img;
  const k = gaussianKernelFixed(sigma); const ksize = k.length; const r = (ksize - 1) / 2;
  const refl = (i, n) => { while (i < 0 || i >= n) { if (i < 0) i = -i; if (i >= n) i = 2 * n - 2 - i; } return i; };
  const tmp = new Int32Array(w * h * 3);
  const xIdx = new Int32Array(w + 2 * r);
  for (let i = -r; i < w + r; i++) xIdx[i + r] = refl(i, w);
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      let a0 = 0, a1 = 0, a2 = 0;
      for (let t = 0; t < ksize; t++) {
        const kv = k[t]; if (kv === 0) continue;
        const q = (y * w + xIdx[x + t]) * 3;
        a0 += data[q] * kv; a1 += data[q + 1] * kv; a2 += data[q + 2] * kv;
      }
      const o = (y * w + x) * 3; tmp[o] = a0; tmp[o + 1] = a1; tmp[o + 2] = a2;
    }
  }
  const out = new Uint8Array(w * h * 3);
  const yIdx = new Int32Array(h + 2 * r);
  for (let i = -r; i < h + r; i++) yIdx[i + r] = refl(i, h);
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      let a0 = 0, a1 = 0, a2 = 0;
      for (let t = 0; t < ksize; t++) {
        const kv = k[t]; if (kv === 0) continue;
        const q = (yIdx[y + t] * w + x) * 3;
        a0 += tmp[q] * kv; a1 += tmp[q + 1] * kv; a2 += tmp[q + 2] * kv;
      }
      const o = (y * w + x) * 3;
      out[o] = Math.min(255, Math.floor((a0 + 32768) / 65536));
      out[o + 1] = Math.min(255, Math.floor((a1 + 32768) / 65536));
      out[o + 2] = Math.min(255, Math.floor((a2 + 32768) / 65536));
    }
  }
  return out;
}

/** ben_graham_uint8: crop -> resize 512 -> 4*img - 4*blur + 128 -> circle mask (r = 0.95*256). */
export function benGrahamUint8(img, size = CACHE_SIZE) {
  const cropped = cropImageFromGray(img);
  if (cropped.width < 2 || cropped.height < 2) throw new Error('Ben Graham crop produced an empty image');
  const resized = resizeBilinearCv(cropped, size, size);
  const blur = gaussianBlur(resized);
  const out = new Uint8Array(size * size * 3);
  const cx = size >> 1, cy = size >> 1; const radius = Math.trunc(Math.min(cx, cy) * 0.95);
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const inside = (x - cx) ** 2 + (y - cy) ** 2 <= radius * radius;
      for (let c = 0; c < 3; c++) {
        const o = (y * size + x) * 3 + c;
        const blurU8 = blur[o];
        out[o] = inside ? Math.min(255, Math.max(0, Math.round(4 * resized.data[o] - 4 * blurU8 + 128))) : 128;
      }
    }
  }
  return { data: out, width: size, height: size };
}

/** PIL Image.resize(..., BILINEAR) with PIL's antialiasing support and 8-bit fixed point
 * (ImagingResample: horizontal pass then vertical pass, PRECISION_BITS = 22). */
export function resizePilBilinear(img, ow, oh) {
  let cur = img;
  if (ow !== cur.width) cur = pilPass(cur, ow, true);
  if (oh !== cur.height) cur = pilPass(cur, oh, false);
  return cur;
}

function pilCoeffs(inSize, outSize) {
  const scale = inSize / outSize; const filterscale = Math.max(scale, 1);
  const support = 1.0 * filterscale; const ksize = Math.ceil(support) * 2 + 1;
  const bounds = []; const kk = [];
  for (let xx = 0; xx < outSize; xx++) {
    const center = (xx + 0.5) * scale; const ss = 1 / filterscale;
    let xmin = Math.trunc(center - support + 0.5); if (xmin < 0) xmin = 0;
    let xmax = Math.trunc(center + support + 0.5); if (xmax > inSize) xmax = inSize; xmax -= xmin;
    const k = new Float64Array(ksize); let ww = 0;
    for (let x = 0; x < xmax; x++) {
      let t = (x + xmin - center + 0.5) * ss; t = t < 0 ? -t : t;
      const w = t < 1 ? 1 - t : 0; k[x] = w; ww += w;
    }
    const ik = new Int32Array(ksize);
    for (let x = 0; x < xmax; x++) {
      const v = ww !== 0 ? k[x] / ww : k[x];
      ik[x] = v < 0 ? Math.trunc(-0.5 + v * (1 << 22)) : Math.trunc(0.5 + v * (1 << 22));
    }
    bounds.push([xmin, xmax]); kk.push(ik);
  }
  return { bounds, kk };
}

function pilPass(img, outSize, horizontal) {
  const { data, width: iw, height: ih } = img;
  const { bounds, kk } = pilCoeffs(horizontal ? iw : ih, outSize);
  const ow = horizontal ? outSize : iw, oh = horizontal ? ih : outSize;
  const out = new Uint8Array(ow * oh * 3); const half = 1 << 21;
  for (let y = 0; y < oh; y++) {
    for (let x = 0; x < ow; x++) {
      const [mn, n] = bounds[horizontal ? x : y]; const k = kk[horizontal ? x : y];
      for (let c = 0; c < 3; c++) {
        let ss = half;
        for (let t = 0; t < n; t++) {
          const q = horizontal ? (y * iw + mn + t) * 3 + c : ((mn + t) * iw + x) * 3 + c;
          ss += data[q] * k[t];
        }
        // ss can exceed 2^31 only for > 255 sums which clip anyway; use Math to stay exact
        let v = Math.floor(ss / 4194304);
        out[(y * ow + x) * 3 + c] = v < 0 ? 0 : v > 255 ? 255 : v;
      }
    }
  }
  return { data: out, width: ow, height: oh };
}

/** 448 RGB uint8 -> NCHW Float32 ImageNet-normalised tensor data (+ its horizontal flip). */
export function toNchwNormalized(img, flip = false) {
  const { data, width: w, height: h } = img;
  const out = new Float32Array(3 * w * h);
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      const sxp = flip ? w - 1 - x : x; const q = (y * w + sxp) * 3;
      for (let c = 0; c < 3; c++) out[c * w * h + y * w + x] = (data[q + c] / 255 - MEAN[c]) / STD[c];
    }
  }
  return out;
}

/** Gate input: PIL convert RGB -> resize 224 BILINEAR, float [0,255] NHWC. */
export function gateInput(img) {
  const r = resizePilBilinear(img, GATE_SIZE, GATE_SIZE);
  return Float32Array.from(r.data);
}

/**
 * Full student input pipeline. `jpegRoundtrip(rgbImg) -> Promise<rgbImg>` re-encodes at q92.
 * Returns {input, inputFlipped, cache512}.
 */
export async function studentInputs(img, jpegRoundtrip) {
  const reduced = reduceLikeCache(img);
  const bg = benGrahamUint8(reduced);
  const cache512 = jpegRoundtrip ? await jpegRoundtrip(bg) : bg;
  const x448 = resizePilBilinear(cache512, INPUT_SIZE, INPUT_SIZE);
  return { input: toNchwNormalized(x448, false), inputFlipped: toNchwNormalized(x448, true), cache512 };
}

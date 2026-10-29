import 'dart:io';
import 'dart:typed_data';

import 'package:dr_fundus_mobile/core/lite/lite_preprocess.dart';
import 'package:flutter_test/flutter_test.dart';

/// Optional parity check of the Dart preprocessing against python_reference.py.
/// Run:  LITE_PARITY_DIR=/dir/with/ref.json.*.input.npy LITE_PARITY_IMAGES="a.jpg b.jpg" \
///       flutter test test/lite_preprocess_parity_test.dart
/// Also writes <dir>/dart.<image>[.flip].nhwc.f32 so the TFLite model can be run on exactly
/// the Dart tensors in Python (dr-fundus-app/lite_parity/tflite_on_dart_inputs.py).
void main() {
  final dir = Platform.environment['LITE_PARITY_DIR'];
  final images = (Platform.environment['LITE_PARITY_IMAGES'] ?? '').split(' ').where((s) => s.isNotEmpty).toList();

  test('Gaussian kernel is OpenCV bit-exact shape (sum 256, 121 taps)', () {
    final k = LitePreprocess.gaussianKernelFixed();
    expect(k.length, 121);
    expect(k.reduce((a, b) => a + b), 256);
  });

  test('Dart preprocessing vs Python', () {
    if (dir == null || images.isEmpty) {
      markTestSkipped('LITE_PARITY_DIR / LITE_PARITY_IMAGES not set');
      return;
    }
    for (final f in images) {
      final name = f.split('/').last;
      final im = LitePreprocess.decode(File(f).readAsBytesSync())!;
      final r = LitePreprocess.studentInputs(im);
      File('$dir/dart.$name.nhwc.f32').writeAsBytesSync(r.input.buffer.asUint8List());
      File('$dir/dart.$name.flip.nhwc.f32').writeAsBytesSync(r.flipped.buffer.asUint8List());
      final npy = File('$dir/ref.json.$name.input.npy');
      if (!npy.existsSync()) continue;
      final b = npy.readAsBytesSync();
      final hl = ByteData.sublistView(b, 8, 10).getUint16(0, Endian.little);
      final ref = Float32List.sublistView(Uint8List.fromList(b.sublist(10 + hl))); // NCHW
      var diff = 0.0;
      const s = 448;
      for (var c = 0; c < 3; c++) {
        for (var i = 0; i < s * s; i++) {
          diff += (ref[c * s * s + i] - r.input[i * 3 + c]).abs();
        }
      }
      final mean = diff / ref.length;
      // ignore: avoid_print
      print('$name mean|dart-python| input = ${mean.toStringAsFixed(4)}');
      expect(mean, lessThan(0.08));
    }
  });
}

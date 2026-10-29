import 'dart:isolate';
import 'dart:typed_data';

import 'package:image/image.dart' as img;
import 'package:tflite_flutter/tflite_flutter.dart';

import '../lite/lite_classes.dart';
import '../lite/lite_decode.dart';
import '../lite/lite_preprocess.dart';
import '../../models/dr_prediction.dart';

/// Lite mode: the distilled EfficientNet-B4-448 two-head student (TFLite fp16, 35 MB) running
/// fully on the phone. Same preprocessing (Ben Graham 512 + JPEG q92 + Resize 448 + ImageNet
/// normalisation), flip TTA and decode (hier_ext w1 1.5, t5 0.45, t5n 0.75) as the Python eval.
class LiteInferenceService {
  static final LiteInferenceService _instance = LiteInferenceService._internal();
  factory LiteInferenceService() => _instance;
  LiteInferenceService._internal();

  static const String modelAsset = 'assets/models/student_effb4_twohead_448_fp16.tflite';
  static const String testNote =
      'Mô hình Lite (student EfficientNet-B4-448 hai đầu ra, chưng cất từ ensemble) chạy offline trên điện thoại. '
      'TEST SCORE 0.6820 so với ensemble 0.6861 (API).';

  Interpreter? _interpreter;
  IsolateInterpreter? _isolate;
  String? loadError;

  bool get isReady => _isolate != null;

  Future<void> initialize() async {
    if (_isolate != null) return;
    try {
      final options = InterpreterOptions()..threads = 4;
      _interpreter = await Interpreter.fromAsset(modelAsset, options: options);
      _interpreter!.allocateTensors();
      _isolate = await IsolateInterpreter.create(address: _interpreter!.address);
      loadError = null;
    } catch (e) {
      loadError = 'Không nạp được mô hình Lite ($modelAsset): $e';
      rethrow;
    }
  }

  Future<List<double>> _run(Float32List nhwc) async {
    final out = Float32List(6);
    // Uint8List in = raw float32 bytes (no reshape); ByteBuffer out = copied in place.
    await _isolate!.run(nhwc.buffer.asUint8List(), out.buffer);
    return out.map((v) => v.toDouble()).toList();
  }

  /// Returns the Lite DR prediction (same shape as the API's dr_result) plus the
  /// Ben Graham 512 image (JPEG bytes) that was fed to the model.
  Future<({DRPrediction prediction, Uint8List preprocessedJpeg, List<double> rawProbs})> predict(
      Uint8List imageBytes) async {
    await initialize();
    final prep = await Isolate.run(() => _preprocess(imageBytes));
    final a = await _run(prep.input);
    final b = await _run(prep.flipped);
    final probs = List<double>.generate(6, (i) => (a[i] + b[i]) / 2);
    return (
      prediction: buildPrediction(probs),
      preprocessedJpeg: prep.jpg,
      rawProbs: probs,
    );
  }

  /// Decode + packaging shared with tests: mirrors backend classifier._pack().
  static DRPrediction buildPrediction(List<double> probs) {
    final (stage, q) = LiteDecode.decode(probs);
    final info = LiteClasses.severity[stage]!;
    double r4(double v) => (v * 10000).roundToDouble() / 10000;
    return DRPrediction(
      modelUsed: 'Lite: EfficientNet-B4-448 hai đầu ra (student, TFLite fp16 trên máy)',
      stage: stage,
      stageName: info['title']!,
      badge: info['badge']!,
      confidence: r4(q[stage]),
      description: info['description']!,
      advice: info['advice']!,
      benchmarkNote: '$testNote | decode hier_ext w1=${LiteDecode.w1} t5=${LiteDecode.t5} t5n=${LiteDecode.t5n} '
          '(xác suất hiển thị đã nhân w1 cho lớp 1 rồi chuẩn hóa)',
      probabilities: {for (var i = 0; i < 6; i++) LiteClasses.classes[i]: r4(q[i])},
      branch: 'lite_student',
      weight: 1.0,
      decode: LiteDecode.record,
    );
  }
}

/// Runs in a background isolate (top-level so the closure captures nothing unsendable).
({Float32List input, Float32List flipped, Uint8List jpg}) _preprocess(Uint8List imageBytes) {
  final im = LitePreprocess.decode(imageBytes);
  if (im == null) throw StateError('Không thể giải mã định dạng ảnh!');
  final r = LitePreprocess.studentInputs(im);
  final jpg = Uint8List.fromList(img.encodeJpg(r.cache512.toImage(), quality: 90));
  return (input: r.input, flipped: r.flipped, jpg: jpg);
}

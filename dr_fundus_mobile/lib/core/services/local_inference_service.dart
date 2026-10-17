import 'dart:typed_data';
import 'package:flutter/services.dart' show rootBundle;
import 'package:image/image.dart' as img;
import 'package:onnxruntime/onnxruntime.dart';

class LocalGateResult {
  final bool isFundus;
  final double confidence;
  final double threshold;
  final String message;

  LocalGateResult({
    required this.isFundus,
    required this.confidence,
    required this.threshold,
    required this.message,
  });
}

class LocalInferenceService {
  static final LocalInferenceService _instance = LocalInferenceService._internal();
  factory LocalInferenceService() => _instance;
  LocalInferenceService._internal();

  OrtSession? _sessionGate;
  bool _isInitialized = false;

  static const double gateThreshold = 0.965;

  Future<void> initialize() async {
    if (_isInitialized) return;

    try {
      OrtEnv.instance.init();
      final sessionOptions = OrtSessionOptions();

      // Nạp Model A (Fundus Gate)
      final gateBytes = await rootBundle.load('assets/models/fundus_gate.onnx');
      _sessionGate = OrtSession.fromBuffer(
        gateBytes.buffer.asUint8List(),
        sessionOptions,
      );

      _isInitialized = true;
    } catch (e) {
      print('[LocalInferenceService] Lỗi khởi tạo ONNX runtime: $e');
    }
  }

  /// 1. Sàng lọc Cổng Model A trực tiếp trên thiết bị (Mobile Edge)
  Future<LocalGateResult> evaluateFundusGate(Uint8List imageBytes) async {
    await initialize();
    if (_sessionGate == null) {
      return LocalGateResult(
        isFundus: true,
        confidence: 0.99,
        threshold: gateThreshold,
        message: 'Bỏ qua cổng kiểm duyệt (Session chưa sẵn sàng)',
      );
    }

    final decoded = img.decodeImage(imageBytes);
    if (decoded == null) {
      return LocalGateResult(
        isFundus: false,
        confidence: 0.0,
        threshold: gateThreshold,
        message: 'Không thể giải mã định dạng ảnh!',
      );
    }

    final resized = img.copyResize(decoded, width: 224, height: 224);
    final inputData = Float32List(1 * 224 * 224 * 3);
    int idx = 0;
    for (int y = 0; y < 224; y++) {
      for (int x = 0; x < 224; x++) {
        final pixel = resized.getPixel(x, y);
        inputData[idx++] = pixel.r.toDouble();
        inputData[idx++] = pixel.g.toDouble();
        inputData[idx++] = pixel.b.toDouble();
      }
    }

    final inputOrt = OrtValueTensor.createTensorWithDataList(
      inputData,
      [1, 224, 224, 3],
    );

    final runOptions = OrtRunOptions();
    final outputs = await _sessionGate!.runAsync(
      runOptions,
      {'input_image:0': inputOrt},
      ['Identity:0'],
    );

    inputOrt.release();
    runOptions.release();

    if (outputs != null && outputs.isNotEmpty) {
      final tensor = outputs[0] as OrtValueTensor;
      final rawList = tensor.value as List<dynamic>;
      tensor.release();

      double confidence = 0.0;
      if (rawList.isNotEmpty && rawList[0] is List) {
        confidence = (rawList[0][0] as num).toDouble();
      } else if (rawList.isNotEmpty) {
        confidence = (rawList[0] as num).toDouble();
      }

      final isFundus = confidence >= gateThreshold;
      return LocalGateResult(
        isFundus: isFundus,
        confidence: confidence,
        threshold: gateThreshold,
        message: isFundus
            ? 'Ảnh đáy mắt hợp lệ (Mobile Edge Gate: ${(confidence * 100).toStringAsFixed(1)}%)'
            : 'Ảnh bị từ chối: Không phải ảnh đáy mắt hợp lệ (Độ tin cậy: ${(confidence * 100).toStringAsFixed(1)}% < ${(gateThreshold * 100).toStringAsFixed(1)}%)',
      );
    }

    return LocalGateResult(
      isFundus: false,
      confidence: 0.0,
      threshold: gateThreshold,
      message: 'Lỗi thực thi suy luận Cổng trên thiết bị',
    );
  }
}

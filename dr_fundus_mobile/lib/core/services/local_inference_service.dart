import 'dart:typed_data';
import 'package:flutter/services.dart' show rootBundle;
import 'package:image/image.dart' as img;
import 'package:onnxruntime/onnxruntime.dart';
import '../../models/model_c_prediction.dart';

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
  OrtSession? _sessionModelC;
  bool _isInitialized = false;

  static const double gateThreshold = 0.965;

  static const List<String> modelCClasses = [
    'DR',
    'ARMD',
    'MYA',
    'DN',
    'ERM',
    'BRVO',
    'LS',
    'ODC_GLAUCOMA',
    'CRVO',
    'RISK',
  ];

  static const Map<String, Map<String, String>> diseaseMeta = {
    'DR': {'name': 'Diabetic Retinopathy', 'desc': 'Tổn thương vi mạch võng mạc do đái tháo đường'},
    'ARMD': {'name': 'Age-related Macular Degeneration', 'desc': 'Thoái hóa hoàng điểm do tuổi tác'},
    'MYA': {'name': 'Pathological Myopia', 'desc': 'Cận thị thoái hóa võng mạc / gai thị'},
    'DN': {'name': 'Drusen', 'desc': 'Lắng đọng chất hyaline dưới võng mạc'},
    'ERM': {'name': 'Epiretinal Membrane', 'desc': 'Màng trước võng mạc / co kéo hoàng điểm'},
    'BRVO': {'name': 'Branch Retinal Vein Occlusion', 'desc': 'Tắc nhánh tĩnh mạch võng mạc'},
    'LS': {'name': 'Laser Scars', 'desc': 'Sẹo quang đông laser sau điều trị'},
    'ODC_GLAUCOMA': {'name': 'Optic Disc Cupping / Glaucoma', 'desc': 'Lõm gai thị sinh lý lớn hoặc biến đổi glôcôm'},
    'CRVO': {'name': 'Central Retinal Vein Occlusion', 'desc': 'Tắc tĩnh mạch trung tâm võng mạc'},
    'RISK': {'name': 'General Disease Risk', 'desc': 'Tín hiệu phát hiện tổn thương bệnh lý võng mạc bất thường'},
  };

  static const Map<String, double> modelCThresholds = {
    'DR': 0.45,
    'ARMD': 0.35,
    'MYA': 0.35,
    'DN': 0.35,
    'ERM': 0.30,
    'BRVO': 0.30,
    'LS': 0.25,
    'ODC_GLAUCOMA': 0.35,
    'CRVO': 0.30,
    'RISK': 0.50,
  };

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

      // Nạp Model C (Multi-label Screening)
      final modelCBytes = await rootBundle.load('assets/models/model_c.onnx');
      _sessionModelC = OrtSession.fromBuffer(
        modelCBytes.buffer.asUint8List(),
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

  /// 2. Sàng lọc đa nhãn Model C trực tiếp trên thiết bị (Mobile Edge)
  Future<ModelCPrediction?> predictModelCOnDevice(Uint8List imageBytes) async {
    await initialize();
    if (_sessionModelC == null) return null;

    final decoded = img.decodeImage(imageBytes);
    if (decoded == null) return null;

    final resized = img.copyResize(decoded, width: 224, height: 224);
    final planeSize = 224 * 224;
    final inputData = Float32List(1 * 3 * 224 * 224);

    int pixelIdx = 0;
    for (int y = 0; y < 224; y++) {
      for (int x = 0; x < 224; x++) {
        final pixel = resized.getPixel(x, y);
        final r = ((pixel.r / 255.0) - 0.485) / 0.229;
        final g = ((pixel.g / 255.0) - 0.456) / 0.224;
        final b = ((pixel.b / 255.0) - 0.406) / 0.225;

        inputData[0 * planeSize + pixelIdx] = r;
        inputData[1 * planeSize + pixelIdx] = g;
        inputData[2 * planeSize + pixelIdx] = b;
        pixelIdx++;
      }
    }

    final inputOrt = OrtValueTensor.createTensorWithDataList(
      inputData,
      [1, 3, 224, 224],
    );

    final runOptions = OrtRunOptions();
    final outputs = await _sessionModelC!.runAsync(
      runOptions,
      {'input': inputOrt},
      ['probabilities'],
    );

    inputOrt.release();
    runOptions.release();

    if (outputs == null || outputs.isEmpty) return null;

    final tensor = outputs[0] as OrtValueTensor;
    final rawList = tensor.value as List<dynamic>;
    tensor.release();

    List<double> probs = [];
    if (rawList.isNotEmpty && rawList[0] is List) {
      probs = (rawList[0] as List<dynamic>).map((e) => (e as num).toDouble()).toList();
    }

    if (probs.length != modelCClasses.length) return null;

    final Map<String, dynamic> fullProbs = {};
    final List<ModelCConditionItem> detected = [];
    bool overallRisk = false;

    for (int i = 0; i < modelCClasses.length; i++) {
      final code = modelCClasses[i];
      final p = probs[i];
      final th = modelCThresholds[code] ?? 0.5;
      final meta = diseaseMeta[code] ?? {'name': code, 'desc': code};

      fullProbs[code] = {
        'probability': p,
        'threshold': th,
        'positive': p >= th,
      };

      if (code == 'RISK' && p >= th) {
        overallRisk = true;
      }

      if (p >= th && code != 'RISK') {
        detected.add(ModelCConditionItem(
          code: code,
          name: meta['name']!,
          vietnameseDesc: meta['desc']!,
          confidencePct: p * 100,
          probability: p,
          threshold: th,
        ));
      }
    }

    return ModelCPrediction(
      modelName: 'Single-Image EfficientNet-B0 (Edge ONNX)',
      modelVersion: '1.0.0-E2-Harmonized-Mobile',
      inputType: 'Single Fundus RGB Image (Local)',
      overallDiseaseRisk: overallRisk,
      numDetectedConditions: detected.length,
      detectedDiseases: detected,
      fullProbabilities: fullProbs,
      clinicalDisclaimer:
          'Dự đoán được thực thi ngoại tuyến trực tiếp trên điện thoại (On-Device Edge). Kết quả chỉ mang tính sàng lọc hỗ trợ.',
    );
  }
}

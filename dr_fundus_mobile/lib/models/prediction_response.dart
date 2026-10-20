import 'dr_prediction.dart';

class PredictionResponse {
  final bool isFundus;
  final double fundusConfidence;
  final double threshold;
  final String message;
  final double? processingTimeMs;
  final Map<String, dynamic>? modelStatus;

  /// Kết quả báo cáo: ensemble 3 mô hình (ViT-B/16-384 0.45, EffB4-448 0.40, EffB4 hai đầu ra 0.15).
  final DRPrediction? drResult;

  /// Các nhánh của ensemble theo thứ tự trong model_b_locked.json.
  final List<DRPrediction>? drBranches;
  final DRPrediction? drVit;
  final DRPrediction? drEffb4;
  final DRPrediction? drTwohead;

  /// Đã bỏ (nhánh ResNet-50 của v2). Server v3 luôn trả null; giữ để đọc lịch sử cũ.
  final DRPrediction? drResnet;
  final Map<String, double>? ensembleWeights;
  final String? drError;
  final String? clinicalDisclaimer;

  PredictionResponse({
    required this.isFundus,
    required this.fundusConfidence,
    required this.threshold,
    required this.message,
    this.processingTimeMs,
    this.modelStatus,
    this.drResult,
    this.drBranches,
    this.drVit,
    this.drEffb4,
    this.drTwohead,
    this.drResnet,
    this.ensembleWeights,
    this.drError,
    this.clinicalDisclaimer,
  });

  /// Danh sách nhánh để hiển thị: ưu tiên dr_branches, nếu không có thì ghép các trường riêng.
  List<DRPrediction> get branches {
    if (drBranches != null && drBranches!.isNotEmpty) return drBranches!;
    return [drVit, drEffb4, drTwohead, drResnet].whereType<DRPrediction>().toList();
  }

  static DRPrediction? _pred(dynamic value) =>
      value is Map ? DRPrediction.fromJson(Map<String, dynamic>.from(value)) : null;

  factory PredictionResponse.fromJson(Map<String, dynamic> json) {
    final rawBranches = json['dr_branches'];
    final rawWeights = json['ensemble_weights'];
    return PredictionResponse(
      isFundus: json['is_fundus'] ?? false,
      fundusConfidence: (json['fundus_confidence'] as num?)?.toDouble() ?? 0.0,
      threshold: (json['threshold'] as num?)?.toDouble() ?? 0.965,
      message: json['message'] ?? '',
      processingTimeMs: (json['processing_time_ms'] as num?)?.toDouble(),
      modelStatus: json['model_status'] is Map<String, dynamic>
          ? json['model_status']
          : null,
      drResult: _pred(json['dr_result']),
      drBranches: rawBranches is List
          ? rawBranches.map(_pred).whereType<DRPrediction>().toList()
          : null,
      drVit: _pred(json['dr_vit']),
      drEffb4: _pred(json['dr_effb4']),
      drTwohead: _pred(json['dr_twohead']),
      drResnet: _pred(json['dr_resnet']),
      ensembleWeights: rawWeights is Map
          ? rawWeights.map((k, v) => MapEntry(k.toString(), (v as num).toDouble()))
          : null,
      drError: json['dr_error'],
      clinicalDisclaimer: json['clinical_disclaimer'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'is_fundus': isFundus,
      'fundus_confidence': fundusConfidence,
      'threshold': threshold,
      'message': message,
      'processing_time_ms': processingTimeMs,
      'model_status': modelStatus,
      'dr_result': drResult?.toJson(),
      'dr_branches': drBranches?.map((b) => b.toJson()).toList(),
      'dr_vit': drVit?.toJson(),
      'dr_effb4': drEffb4?.toJson(),
      'dr_twohead': drTwohead?.toJson(),
      'dr_resnet': drResnet?.toJson(),
      'ensemble_weights': ensembleWeights,
      'dr_error': drError,
      'clinical_disclaimer': clinicalDisclaimer,
    };
  }
}

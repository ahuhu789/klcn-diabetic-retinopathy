import 'dr_prediction.dart';

class PredictionResponse {
  final bool isFundus;
  final double fundusConfidence;
  final double threshold;
  final String message;
  final double? processingTimeMs;
  final Map<String, dynamic>? modelStatus;
  final DRPrediction? drResnet;
  final DRPrediction? drVit;
  final DRPrediction? drResult;
  final String? drError;
  final String? clinicalDisclaimer;

  PredictionResponse({
    required this.isFundus,
    required this.fundusConfidence,
    required this.threshold,
    required this.message,
    this.processingTimeMs,
    this.modelStatus,
    this.drResnet,
    this.drVit,
    this.drResult,
    this.drError,
    this.clinicalDisclaimer,
  });

  factory PredictionResponse.fromJson(Map<String, dynamic> json) {
    return PredictionResponse(
      isFundus: json['is_fundus'] ?? false,
      fundusConfidence: (json['fundus_confidence'] as num?)?.toDouble() ?? 0.0,
      threshold: (json['threshold'] as num?)?.toDouble() ?? 0.965,
      message: json['message'] ?? '',
      processingTimeMs: (json['processing_time_ms'] as num?)?.toDouble(),
      modelStatus: json['model_status'] is Map<String, dynamic>
          ? json['model_status']
          : null,
      drResnet: json['dr_resnet'] != null
          ? DRPrediction.fromJson(json['dr_resnet'])
          : null,
      drVit: json['dr_vit'] != null
          ? DRPrediction.fromJson(json['dr_vit'])
          : null,
      drResult: json['dr_result'] != null
          ? DRPrediction.fromJson(json['dr_result'])
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
      'dr_resnet': drResnet?.toJson(),
      'dr_vit': drVit?.toJson(),
      'dr_result': drResult?.toJson(),
      'dr_error': drError,
      'clinical_disclaimer': clinicalDisclaimer,
    };
  }
}

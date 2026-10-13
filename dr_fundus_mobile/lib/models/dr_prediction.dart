class DRPrediction {
  final String modelUsed;
  final int stage;
  final String stageName;
  final String badge;
  final double confidence;
  final String description;
  final String advice;
  final String benchmarkNote;
  final Map<String, double> probabilities;
  final String? heatmapBase64;

  DRPrediction({
    required this.modelUsed,
    required this.stage,
    required this.stageName,
    required this.badge,
    required this.confidence,
    required this.description,
    required this.advice,
    required this.benchmarkNote,
    required this.probabilities,
    this.heatmapBase64,
  });

  factory DRPrediction.fromJson(Map<String, dynamic> json) {
    Map<String, double> probs = {};
    if (json['probabilities'] != null) {
      json['probabilities'].forEach((k, v) {
        probs[k.toString()] = (v as num).toDouble();
      });
    }

    return DRPrediction(
      modelUsed: json['model_used'] ?? '',
      stage: json['stage'] ?? 0,
      stageName: json['stage_name'] ?? '',
      badge: json['badge'] ?? '',
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
      description: json['description'] ?? '',
      advice: json['advice'] ?? '',
      benchmarkNote: json['benchmark_note'] ?? '',
      probabilities: probs,
      heatmapBase64: json['heatmap_base64'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'model_used': modelUsed,
      'stage': stage,
      'stage_name': stageName,
      'badge': badge,
      'confidence': confidence,
      'description': description,
      'advice': advice,
      'benchmark_note': benchmarkNote,
      'probabilities': probabilities,
      'heatmap_base64': heatmapBase64,
    };
  }
}

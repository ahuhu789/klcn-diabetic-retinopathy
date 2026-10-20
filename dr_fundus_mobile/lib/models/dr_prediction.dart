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

  /// Model B v3: "ensemble", "vit3", "effb4" hoặc "e_twohead". Null với server cũ.
  final String? branch;

  /// Trọng số của nhánh trong ensemble (1.0 cho ensemble). Null với server cũ.
  final double? weight;

  /// Cách giải mã xác suất thành lớp, ví dụ {"family": "hierarchical", "t5": 0.5}.
  final Map<String, dynamic>? decode;

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
    this.branch,
    this.weight,
    this.decode,
  });

  /// Xác suất của lớp [cls]. Server trả khóa dạng "0 - Không bệnh (No DR)";
  /// dữ liệu cũ hoặc mock có thể dùng khóa "0".
  double probFor(int cls) {
    final exact = probabilities[cls.toString()];
    if (exact != null) return exact;
    for (final entry in probabilities.entries) {
      final key = entry.key.trim();
      if (key.startsWith('$cls ') || key.startsWith('$cls-')) return entry.value;
    }
    return 0.0;
  }

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
      branch: json['branch'] as String?,
      weight: (json['weight'] as num?)?.toDouble(),
      decode: json['decode'] is Map ? Map<String, dynamic>.from(json['decode'] as Map) : null,
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
      'branch': branch,
      'weight': weight,
      'decode': decode,
    };
  }
}

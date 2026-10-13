class ModelCConditionItem {
  final String code;
  final String name;
  final String vietnameseDesc;
  final double confidencePct;
  final double? probability;
  final double? threshold;

  ModelCConditionItem({
    required this.code,
    required this.name,
    required this.vietnameseDesc,
    required this.confidencePct,
    this.probability,
    this.threshold,
  });

  factory ModelCConditionItem.fromJson(Map<String, dynamic> json) {
    return ModelCConditionItem(
      code: json['code'] ?? '',
      name: json['name'] ?? '',
      vietnameseDesc: json['vietnamese_desc'] ?? '',
      confidencePct: (json['confidence_pct'] as num?)?.toDouble() ?? 0.0,
      probability: (json['probability'] as num?)?.toDouble(),
      threshold: (json['threshold'] as num?)?.toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'code': code,
      'name': name,
      'vietnamese_desc': vietnameseDesc,
      'confidence_pct': confidencePct,
      'probability': probability,
      'threshold': threshold,
    };
  }
}

class ModelCPrediction {
  final String modelName;
  final String modelVersion;
  final String inputType;
  final bool overallDiseaseRisk;
  final int numDetectedConditions;
  final List<ModelCConditionItem> detectedDiseases;
  final Map<String, dynamic> fullProbabilities;
  final String clinicalDisclaimer;

  ModelCPrediction({
    required this.modelName,
    required this.modelVersion,
    required this.inputType,
    required this.overallDiseaseRisk,
    required this.numDetectedConditions,
    required this.detectedDiseases,
    required this.fullProbabilities,
    required this.clinicalDisclaimer,
  });

  factory ModelCPrediction.fromJson(Map<String, dynamic> json) {
    List<ModelCConditionItem> items = [];
    if (json['detected_diseases'] != null && json['detected_diseases'] is List) {
      items = (json['detected_diseases'] as List)
          .map((e) => ModelCConditionItem.fromJson(e as Map<String, dynamic>))
          .toList();
    }

    return ModelCPrediction(
      modelName: json['model_name'] ?? '',
      modelVersion: json['model_version'] ?? '',
      inputType: json['input_type'] ?? '',
      overallDiseaseRisk: json['overall_disease_risk'] ?? false,
      numDetectedConditions: json['num_detected_conditions'] ?? 0,
      detectedDiseases: items,
      fullProbabilities: json['full_probabilities'] is Map<String, dynamic>
          ? json['full_probabilities']
          : {},
      clinicalDisclaimer: json['clinical_disclaimer'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'model_name': modelName,
      'model_version': modelVersion,
      'input_type': inputType,
      'overall_disease_risk': overallDiseaseRisk,
      'num_detected_conditions': numDetectedConditions,
      'detected_diseases': detectedDiseases.map((e) => e.toJson()).toList(),
      'full_probabilities': fullProbabilities,
      'clinical_disclaimer': clinicalDisclaimer,
    };
  }
}

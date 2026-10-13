import 'dart:convert';
import 'prediction_response.dart';

class ScreeningHistoryItem {
  final String id;
  final String patientName;
  final String patientId;
  final DateTime timestamp;
  final String imagePath;
  final bool isSample;
  final String? sampleFilename;
  final PredictionResponse response;

  ScreeningHistoryItem({
    required this.id,
    required this.patientName,
    required this.patientId,
    required this.timestamp,
    required this.imagePath,
    this.isSample = false,
    this.sampleFilename,
    required this.response,
  });

  factory ScreeningHistoryItem.fromJson(Map<String, dynamic> json) {
    return ScreeningHistoryItem(
      id: json['id'] ?? '',
      patientName: json['patient_name'] ?? 'Khách vãng lai',
      patientId: json['patient_id'] ?? 'BN-${DateTime.now().millisecondsSinceEpoch}',
      timestamp: DateTime.parse(json['timestamp']),
      imagePath: json['image_path'] ?? '',
      isSample: json['is_sample'] ?? false,
      sampleFilename: json['sample_filename'],
      response: PredictionResponse.fromJson(json['response']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'patient_name': patientName,
      'patient_id': patientId,
      'timestamp': timestamp.toIso8601String(),
      'image_path': imagePath,
      'is_sample': isSample,
      'sample_filename': sampleFilename,
      'response': response.toJson(),
    };
  }

  String serialize() => jsonEncode(toJson());

  static ScreeningHistoryItem deserialize(String str) =>
      ScreeningHistoryItem.fromJson(jsonDecode(str));
}

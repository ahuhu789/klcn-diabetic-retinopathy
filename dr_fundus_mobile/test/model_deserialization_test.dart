import 'package:flutter_test/flutter_test.dart';
import 'package:dr_fundus_mobile/models/prediction_response.dart';
import 'package:dr_fundus_mobile/models/sample_image_info.dart';
import 'package:dr_fundus_mobile/models/screening_history_item.dart';

void main() {
  group('Model Deserialization Tests matching FastAPI Schemas', () {
    test('1. Test PredictionResponse with valid DR Stage 3 response', () {
      final mockJson = {
        'is_fundus': true,
        'fundus_confidence': 1.0,
        'threshold': 0.965,
        'message': 'Ảnh đáy mắt hợp lệ',
        'processing_time_ms': 2276.17,
        'model_status': {'model_a': 'ready', 'model_b': 'ready'},
        'dr_result': {
          'model_used': 'Ensemble ResNet 0.25 + ViT 0.75',
          'stage': 3,
          'stage_name': 'Muc do Nang',
          'badge': 'Mức độ Nặng',
          'confidence': 0.85,
          'description': 'Nhiều xuất huyết võng mạc vi mạch',
          'advice': 'Cần khám chuyên khoa mắt',
          'benchmark_note': 'Ensemble 6 lớp',
          'probabilities': {'0': 0.01, '1': 0.02, '2': 0.05, '3': 0.85, '4': 0.04, '5': 0.03},
          'heatmap_base64': 'data:image/jpeg;base64,/9j/4AAQSkZJRg==',
        },
        'clinical_disclaimer': 'Bản quyền HUIT KLCN',
      };

      final response = PredictionResponse.fromJson(mockJson);

      expect(response.isFundus, isTrue);
      expect(response.fundusConfidence, 1.0);
      expect(response.threshold, 0.965);
      expect(response.drResult, isNotNull);
      expect(response.drResult!.stage, 3);
      expect(response.drResult!.probabilities['3'], 0.85);
      expect(response.drResult!.probabilities.length, 6);
    });

    test('2. Test Model A Gate Rejection response', () {
      final mockJson = {
        'is_fundus': false,
        'fundus_confidence': 0.0761,
        'threshold': 0.965,
        'message': 'Ảnh bị từ chối: Không phải ảnh đáy võng mạc hợp lệ',
        'processing_time_ms': 54.2,
        'dr_result': null,
      };

      final response = PredictionResponse.fromJson(mockJson);

      expect(response.isFundus, isFalse);
      expect(response.fundusConfidence, lessThan(0.965));
      expect(response.drResult, isNull);
    });

    test('3. Test SampleImageInfo parsing', () {
      final sampleJson = {
        'id': 'ARMD_001.jpg',
        'filename': 'ARMD_001.jpg',
        'name': 'Thoái hóa Hoàng điểm Tuổi già (AMD)',
        'category': 'Bệnh võng mạc khác',
        'tag': 'AMD',
        'badge_color': 'amber',
        'description': 'Tổn thương thoái hóa hoàng điểm',
        'url': '/api/samples/ARMD_001.jpg',
      };

      final sample = SampleImageInfo.fromJson(sampleJson);

      expect(sample.id, 'ARMD_001.jpg');
      expect(sample.name, contains('AMD'));
      expect(sample.category, 'Bệnh võng mạc khác');
      expect(sample.badgeColor, 'amber');
    });

    test('4. Test ScreeningHistoryItem serialization & deserialization', () {
      final res = PredictionResponse(
        isFundus: true,
        fundusConfidence: 0.999,
        threshold: 0.965,
        message: 'Thành công',
      );

      final item = ScreeningHistoryItem(
        id: 'REC-001',
        patientName: 'Nguyễn Văn A',
        patientId: 'BN-12345',
        timestamp: DateTime(2026, 10, 12, 10, 30),
        imagePath: '/path/to/img.jpg',
        response: res,
      );

      final serialized = item.serialize();
      final restored = ScreeningHistoryItem.deserialize(serialized);

      expect(restored.id, 'REC-001');
      expect(restored.patientName, 'Nguyễn Văn A');
      expect(restored.response.isFundus, isTrue);
    });
  });
}

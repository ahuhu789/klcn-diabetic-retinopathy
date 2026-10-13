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
        'model_status': {'model_a': 'ready', 'model_b': 'ready', 'model_c': 'ready'},
        'dr_result': {
          'model_used': 'ViT-B/16 & ResNet-50 Hybrid',
          'stage': 3,
          'stage_name': 'Muc do Nang',
          'badge': 'Mức độ Nặng (Tiền tăng sinh)',
          'confidence': 0.85,
          'description': 'Nhiều xuất huyết võng mạc vi mạch',
          'advice': 'Cần can thiệp chuyên khoa mắt khẩn trương',
          'benchmark_note': 'Hybrid Ordinal Staging',
          'probabilities': {'0': 0.01, '1': 0.04, '2': 0.1, '3': 0.85, '4': 0.0},
          'heatmap_base64': 'data:image/jpeg;base64,/9j/4AAQSkZJRg==',
        },
        'model_c_result': {
          'model_name': 'EfficientNet-B0 E2',
          'model_version': 'E2',
          'input_type': 'Single Fundus Image',
          'overall_disease_risk': true,
          'num_detected_conditions': 1,
          'detected_diseases': [
            {
              'code': 'DR',
              'name': 'Diabetic Retinopathy',
              'vietnamese_desc': 'Bệnh võng mạc đái tháo đường',
              'confidence_pct': 96.07,
              'probability': 0.9607,
              'threshold': 0.16,
            }
          ],
          'full_probabilities': {
            'DR': {
              'name': 'Diabetic Retinopathy',
              'probability': 0.9607,
              'threshold': 0.16,
              'detected': true,
            },
            'ARMD': {
              'name': 'Age-related Macular Degeneration',
              'probability': 0.05,
              'threshold': 0.28,
              'detected': false,
            }
          },
          'clinical_disclaimer': 'Nghiên cứu học thuật KLCN',
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
      expect(response.modelCResult, isNotNull);
      expect(response.modelCResult!.overallDiseaseRisk, isTrue);
      expect(response.modelCResult!.detectedDiseases.length, 1);
      expect(response.modelCResult!.detectedDiseases.first.code, 'DR');
    });

    test('2. Test Model A Gate Rejection response', () {
      final mockJson = {
        'is_fundus': false,
        'fundus_confidence': 0.0761,
        'threshold': 0.965,
        'message': 'Ảnh bị từ chối: Không phải ảnh đáy võng mạc hợp lệ',
        'processing_time_ms': 54.2,
        'dr_result': null,
        'model_c_result': null,
      };

      final response = PredictionResponse.fromJson(mockJson);

      expect(response.isFundus, isFalse);
      expect(response.fundusConfidence, lessThan(0.965));
      expect(response.drResult, isNull);
      expect(response.modelCResult, isNull);
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

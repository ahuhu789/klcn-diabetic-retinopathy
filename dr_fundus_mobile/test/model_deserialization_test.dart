import 'package:flutter_test/flutter_test.dart';
import 'package:dr_fundus_mobile/models/prediction_response.dart';
import 'package:dr_fundus_mobile/models/sample_image_info.dart';
import 'package:dr_fundus_mobile/models/screening_history_item.dart';

Map<String, dynamic> _branch(String key, double weight, int stage) => {
      'model_used': key,
      'stage': stage,
      'stage_name': 'Lớp $stage',
      'badge': 'Lớp $stage',
      'confidence': 0.8,
      'description': '',
      'advice': '',
      'benchmark_note': '',
      'probabilities': {
        '0 - Không bệnh (No DR)': 0.02,
        '1 - Nhẹ (Mild NPDR)': 0.03,
        '2 - Trung bình (Moderate NPDR)': 0.05,
        '3 - Nặng (Severe NPDR)': 0.8,
        '4 - Tăng sinh (Proliferative DR)': 0.05,
        '5 - Tổn thương không phải DR': 0.05,
      },
      'heatmap_base64': 'data:image/jpeg;base64,/9j/4AAQSkZJRg==',
      'branch': key,
      'weight': weight,
      'decode': {'family': 'hierarchical', 't5': 0.475},
    };

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
          'model_used': 'Ensemble ViT-B/16-384 v3 0.45 + EfficientNet-B4-448 v3 0.40 + EfficientNet-B4-448 two-head (Pha E) 0.15',
          'branch': 'ensemble',
          'weight': 1.0,
          'decode': {'family': 'hierarchical', 't5': 0.5, 'thresholds': null},
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
        'dr_branches': [
          _branch('vit3', 0.45, 3),
          _branch('effb4', 0.40, 3),
          _branch('e_twohead', 0.15, 2),
        ],
        'dr_vit': _branch('vit3', 0.45, 3),
        'dr_effb4': _branch('effb4', 0.40, 3),
        'dr_twohead': _branch('e_twohead', 0.15, 2),
        'dr_resnet': null,
        'ensemble_weights': {'vit3': 0.45, 'effb4': 0.4, 'e_twohead': 0.15},
        'clinical_disclaimer': 'Bản quyền HUIT KLCN',
      };

      final response = PredictionResponse.fromJson(mockJson);
      expect(response.drResnet, isNull);
      expect(response.branches.length, 3);
      expect(response.branches.map((b) => b.branch).toList(), ['vit3', 'effb4', 'e_twohead']);
      expect(response.drTwohead!.stage, 2);
      expect(response.ensembleWeights!['effb4'], 0.4);
      expect(response.drResult!.decode!['t5'], 0.5);
      // Server keys look like "0 - Không bệnh (No DR)"; probFor must find them.
      expect(response.drVit!.probFor(3), 0.8);
      expect(response.drVit!.probFor(5), 0.05);
      final roundTrip = PredictionResponse.fromJson(response.toJson());
      expect(roundTrip.branches.length, 3);
      expect(roundTrip.drResult!.probFor(3), 0.85);

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
      expect(response.branches, isEmpty);
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

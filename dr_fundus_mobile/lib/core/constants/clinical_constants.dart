class ClinicalConstants {
  // Lớp 0-4 là thang DR. Lớp 5 là nhóm tổn thương không phải DR.
  static const Map<int, String> drStageNames = {
    0: 'Bình thường (No DR)',
    1: 'Nhẹ (Mild NPDR)',
    2: 'Trung bình (Moderate NPDR)',
    3: 'Nặng (Severe NPDR)',
    4: 'Tăng sinh (Proliferative DR)',
    5: 'Tổn thương không phải DR',
  };

  static const Map<int, String> drDescriptions = {
    0: 'Không phát hiện dấu hiệu bệnh võng mạc đái tháo đường.',
    1: 'Chỉ xuất hiện các vi phình mạch (Microaneurysms) đơn độc.',
    2: 'Xuất hiện vi phình mạch, xuất huyết điểm hoặc xuất tiết cứng mức độ vừa.',
    3: 'Xuất huyết võng mạc nhiều ở 4 góc phần tư, tĩnh mạch chuỗi hạt hoặc IRMA.',
    4: 'Tân mạch võng mạc (Neovascularization) hoặc xuất huyết dịch kính nghiêm trọng.',
    5: 'Nhóm chung cho tổn thương không thuộc thang DR. Không nêu tên từng bệnh.',
  };

  static const Map<int, String> drAdvice = {
    0: 'Khám mắt định kỳ 12 tháng/lần, kiểm soát tốt chỉ số HbA1c và đường huyết.',
    1: 'Theo dõi đáy mắt 6 - 9 tháng/lần, duy trì chế độ ăn kiêng và tập luyện phù hợp.',
    2: 'Tái khám chuyên khoa mắt mỗi 3 - 6 tháng, tham khảo ý kiến bác sĩ nội tiết.',
    3: 'Cần can thiệp chuyên khoa đáy mắt khẩn trương (laser quang đông hoặc anti-VEGF).',
    4: 'Cần khám chuyên khoa mắt sớm. Kết quả này không phải chỉ định phẫu thuật.',
    5: 'Nhờ bác sĩ mắt xem ảnh. Không tự gắn tên bệnh từ lớp 5.',
  };

  // Model B v3 (khóa trên tập validation): ensemble 3 mô hình, giải mã phân tầng.
  // Lớp 5 nếu p5 > t5, ngược lại argmax của 5 lớp DR.
  static const Map<String, double> ensembleWeights = {
    'vit3': 0.45,
    'effb4': 0.40,
    'e_twohead': 0.15,
  };
  static const Map<String, String> branchLabels = {
    'ensemble': 'Ensemble',
    'vit3': 'ViT-B/16-384',
    'effb4': 'EfficientNet-B4-448',
    'e_twohead': 'EffB4 hai đầu ra',
    'vit': 'ViT-B/16 (v2, đã bỏ)',
    'resnet': 'ResNet-50 (v2, đã bỏ)',
  };
  static const double hierarchicalT5 = 0.50;

  // Số liệu TEST (8818 ảnh, chấm một lần sau khi khóa trên VAL).
  static const String testMetricsSummary =
      'TEST n=8818: Acc 79.36%, macro-F1 0.6151, QWK_DR 0.7572, SCORE 0.6861 (CI95 0.6684–0.7035).';

  // Tuyên bố miễn trừ trách nhiệm y khoa
  static const String clinicalDisclaimer =
      'CẢNH BÁO Y KHOA: Hệ thống AI RetinaGuard Mobile được phát triển phục vụ mục đích nghiên cứu học thuật và hỗ trợ sàng lọc sơ bộ tại điểm khám. Kết quả dự đoán KHÔNG THAY THẾ cho chẩn đoán của bác sĩ chuyên khoa mắt. Mọi quyết định can thiệp lâm sàng cần được thăm khám trực tiếp bởi bác sĩ nhãn khoa.';
}

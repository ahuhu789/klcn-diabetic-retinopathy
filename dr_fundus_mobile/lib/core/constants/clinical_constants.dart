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

  // Ngưỡng SCORE đã chọn của lần train 6 lớp.
  static const List<double> ordinalThresholds = [0.95, 1.35, 2.35, 3.15];

  // Tuyên bố miễn trừ trách nhiệm y khoa
  static const String clinicalDisclaimer =
      'CẢNH BÁO Y KHOA: Hệ thống AI RetinaGuard Mobile được phát triển phục vụ mục đích nghiên cứu học thuật và hỗ trợ sàng lọc sơ bộ tại điểm khám. Kết quả dự đoán KHÔNG THAY THẾ cho chẩn đoán của bác sĩ chuyên khoa mắt. Mọi quyết định can thiệp lâm sàng cần được thăm khám trực tiếp bởi bác sĩ nhãn khoa.';
}

class ClinicalConstants {
  // Thang phân độ 5 cấp ICDR Diabetic Retinopathy
  static const Map<int, String> drStageNames = {
    0: 'Bình thường (No DR)',
    1: 'Nhẹ (Mild NPDR)',
    2: 'Trung bình (Moderate NPDR)',
    3: 'Nặng (Severe NPDR)',
    4: 'Tăng sinh (Proliferative DR)',
  };

  static const Map<int, String> drDescriptions = {
    0: 'Không phát hiện dấu hiệu bệnh võng mạc đái tháo đường.',
    1: 'Chỉ xuất hiện các vi phình mạch (Microaneurysms) đơn độc.',
    2: 'Xuất hiện vi phình mạch, xuất huyết điểm hoặc xuất tiết cứng mức độ vừa.',
    3: 'Xuất huyết võng mạc nhiều ở 4 góc phần tư, tĩnh mạch chuỗi hạt hoặc IRMA.',
    4: 'Tân mạch võng mạc (Neovascularization) hoặc xuất huyết dịch kính nghiêm trọng.',
  };

  static const Map<int, String> drAdvice = {
    0: 'Khám mắt định kỳ 12 tháng/lần, kiểm soát tốt chỉ số HbA1c và đường huyết.',
    1: 'Theo dõi đáy mắt 6 - 9 tháng/lần, duy trì chế độ ăn kiêng và tập luyện phù hợp.',
    2: 'Tái khám chuyên khoa mắt mỗi 3 - 6 tháng, tham khảo ý kiến bác sĩ nội tiết.',
    3: 'Cần can thiệp chuyên khoa đáy mắt khẩn trương (laser quang đông hoặc anti-VEGF).',
    4: 'Cần điều trị can thiệp chuyên khoa mắt ngay lập tức để phòng ngừa mất thị lực vĩnh viễn.',
  };

  // Từ điển 10 bệnh lý võng mạc Model C
  static const Map<String, Map<String, String>> diseaseInfo = {
    'DR': {
      'name': 'Bệnh võng mạc đái tháo đường',
      'en': 'Diabetic Retinopathy',
      'category': 'Mạch máu',
      'desc': 'Tổn thương mao mạch võng mạc do biến chứng đái tháo đường kéo dài.',
    },
    'ARMD': {
      'name': 'Thoái hóa hoàng điểm tuổi già',
      'en': 'Age-related Macular Degeneration',
      'category': 'Hoàng điểm',
      'desc': 'Thoái hóa tế bào biểu mô sắc tố hoàng điểm kèm lắng đọng Drusen.',
    },
    'MYA': {
      'name': 'Cận thị bệnh lý thoái hóa',
      'en': 'Pathological Myopia',
      'category': 'Khúc xạ',
      'desc': 'Trục nhãn cầu kéo dài gây thoái hóa hắc võng mạc và liềm quanh gai thị.',
    },
    'DN': {
      'name': 'Lắng đọng Drusen võng mạc',
      'en': 'Drusen Deposits',
      'category': 'Lắng đọng',
      'desc': 'Lắng đọng chất cặn bã chuyển hóa màu vàng dưới lớp biểu mô sắc tố.',
    },
    'ERM': {
      'name': 'Màng trước võng mạc',
      'en': 'Epiretinal Membrane',
      'category': 'Co kéo',
      'desc': 'Lớp màng xơ co kéo trên bề mặt hoàng điểm làm biến dạng thị lực.',
    },
    'BRVO': {
      'name': 'Tắc nhánh tĩnh mạch võng mạc',
      'en': 'Branch Retinal Vein Occlusion',
      'category': 'Tắc mạch',
      'desc': 'Tắc nghẽn một nhánh tĩnh mạch dẫn lưu máu gây xuất huyết dạng ngọn lửa.',
    },
    'LS': {
      'name': 'Sẹo quang đông Laser',
      'en': 'Laser Photocoagulation Scars',
      'category': 'Điều trị',
      'desc': 'Các vết sẹo do can thiệp laser quang đông điều trị thiếu máu võng mạc.',
    },
    'ODC_GLAUCOMA': {
      'name': 'Lõm gai thị / Biến đổi Glôcôm',
      'en': 'Optic Disc Cupping / Glaucoma',
      'category': 'Gai thị',
      'desc': 'Lõm đĩa thị giác rộng bất thường gợi ý tổn thương teo sợi thần kinh thị.',
    },
    'CRVO': {
      'name': 'Tắc tĩnh mạch trung tâm võng mạc',
      'en': 'Central Retinal Vein Occlusion',
      'category': 'Tắc mạch',
      'desc': 'Tắc nghẽn toàn bộ thân tĩnh mạch trung tâm gây xuất huyết rầm rộ toàn đáy mắt.',
    },
    'RISK': {
      'name': 'Cảnh báo rủi ro bệnh học chung',
      'en': 'General Retinal Disease Risk',
      'category': 'Sàng lọc',
      'desc': 'Cờ sàng lọc phát hiện bất kỳ dấu hiệu tổn thương nào trên ảnh đáy mắt.',
    },
  };

  // Ngưỡng phân chia thứ tự Model B
  static const List<double> ordinalThresholds = [0.9500, 1.6759, 2.0500, 3.2500];

  // Tuyên bố miễn trừ trách nhiệm y khoa
  static const String clinicalDisclaimer =
      'CẢNH BÁO Y KHOA: Hệ thống AI RetinaGuard Mobile được phát triển phục vụ mục đích nghiên cứu học thuật và hỗ trợ sàng lọc sơ bộ tại điểm khám. Kết quả dự đoán KHÔNG THAY THẾ cho chẩn đoán của bác sĩ chuyên khoa mắt. Mọi quyết định can thiệp lâm sàng cần được thăm khám trực tiếp bởi bác sĩ nhãn khoa.';
}

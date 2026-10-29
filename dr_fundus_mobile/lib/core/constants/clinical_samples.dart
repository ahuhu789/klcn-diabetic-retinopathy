import '../../models/sample_image_info.dart';

/// Ten clinical fundus photos bundled with the app, same set as the backend
/// catalog. They can be opened without a server.
class ClinicalSamples {
  static const String _dir = 'assets/samples';

  static final List<SampleImageInfo> all = [
    _sample(
      'NORMAL_001.jpg',
      name: 'Mắt Khỏe mạnh (Bình thường)',
      category: 'Khỏe mạnh',
      tag: 'Bình thường',
      badgeColor: 'emerald',
      description:
          'Ảnh đáy võng mạc bình thường, không có tổn thương mạch máu, hoàng điểm và gai thị nguyên vẹn.',
    ),
    _sample(
      'ARMD_001.jpg',
      name: 'Thoái hóa Hoàng điểm Tuổi già (AMD)',
      category: 'Bệnh võng mạc khác',
      tag: 'AMD',
      badgeColor: 'amber',
      description:
          'Tổn thương thoái hóa hoàng điểm, kèm Drusen và biến đổi tế bào biểu mô sắc tố võng mạc.',
    ),
    _sample(
      'GLAUCOMA_001.jpg',
      name: 'Glaucoma / Lõm đĩa thị (ODC)',
      category: 'Bệnh võng mạc khác',
      tag: 'Glaucoma / ODC',
      badgeColor: 'purple',
      description:
          'Tỷ lệ lõm gai thị Cup-to-Disc mở rộng, gợi ý tổn thương teo gai thị giác do bệnh glôcôm.',
    ),
    _sample(
      'MYA_001.jpg',
      name: 'Cận thị Bệnh lý (Pathological Myopia)',
      category: 'Bệnh võng mạc khác',
      tag: 'Cận thị (MYA)',
      badgeColor: 'blue',
      description:
          'Biến dạng trục nhãn cầu, thoái hóa hắc võng mạc và liềm cận thị điển hình quanh gai thị.',
    ),
    _sample(
      'BRVO_001.jpg',
      name: 'Tắc Nhánh Tĩnh mạch Võng mạc (BRVO)',
      category: 'Bệnh võng mạc khác',
      tag: 'Tắc mạch (BRVO)',
      badgeColor: 'rose',
      description:
          'Xuất huyết dạng ngọn lửa và phù nề dọc theo phân nhánh tĩnh mạch thái dương bị tắc nghẽn.',
    ),
    _sample(
      'DR0_EyePACS_40927_left.jpg',
      name: 'DR cấp 0 – Không bệnh (EyePACS)',
      category: 'Khỏe mạnh',
      tag: 'DR cấp 0',
      badgeColor: 'emerald',
      description: 'Ảnh tập test chính thức (EyePACS 40927_left), nhãn gốc: cấp 0, không có tổn thương DR.',
    ),
    _sample(
      'DR1_EyePACS_36566_left.jpg',
      name: 'DR cấp 1 – Nhẹ (EyePACS)',
      category: 'Đái tháo đường (DR)',
      tag: 'DR cấp 1 (Nhẹ)',
      badgeColor: 'amber',
      description: 'Ảnh tập test chính thức (EyePACS 36566_left), nhãn gốc: cấp 1, vi phình mạch đơn lẻ.',
    ),
    _sample(
      'DR2_EyePACS_31305_left.jpg',
      name: 'DR cấp 2 – Trung bình (EyePACS)',
      category: 'Đái tháo đường (DR)',
      tag: 'DR cấp 2 (Vừa)',
      badgeColor: 'orange',
      description: 'Ảnh tập test chính thức (EyePACS 31305_left), nhãn gốc: cấp 2, xuất huyết và xuất tiết rải rác.',
    ),
    _sample(
      'DR3_EyePACS_27224_right.jpg',
      name: 'DR cấp 3 – Nặng (EyePACS)',
      category: 'Đái tháo đường (DR)',
      tag: 'DR cấp 3 (Nặng)',
      badgeColor: 'red',
      description: 'Ảnh tập test chính thức (EyePACS 27224_right), nhãn gốc: cấp 3, xuất huyết lan tỏa nhiều góc phần tư.',
    ),
    _sample(
      'DR4_EyePACS_4086_left.jpg',
      name: 'DR cấp 4 – Tăng sinh (EyePACS)',
      category: 'Đái tháo đường (DR)',
      tag: 'DR cấp 4 (Tăng sinh)',
      badgeColor: 'red',
      description: 'Ảnh tập test chính thức (EyePACS 4086_left), nhãn gốc: cấp 4, có tân mạch.',
    ),
  ];

  static SampleImageInfo _sample(
    String filename, {
    required String name,
    required String category,
    required String tag,
    required String badgeColor,
    required String description,
  }) {
    return SampleImageInfo(
      id: filename,
      filename: filename,
      name: name,
      category: category,
      tag: tag,
      badgeColor: badgeColor,
      description: description,
      url: '$_dir/$filename',
    );
  }
}

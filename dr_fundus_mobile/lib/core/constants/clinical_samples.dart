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
      'IDRiD_001.jpg',
      name: 'Võng mạc Tiểu đường Nặng (Stage 3)',
      category: 'Đái tháo đường (DR)',
      tag: 'DR Cấp 3 (Nặng)',
      badgeColor: 'red',
      description:
          'Nhiều xuất huyết võng mạc sâu, xuất tiết cứng và vi phình mạch lan tỏa ở 4 góc phần tư.',
    ),
    _sample(
      'IDRiD_002.jpg',
      name: 'Võng mạc Tiểu đường Vừa (Stage 2)',
      category: 'Đái tháo đường (DR)',
      tag: 'DR Cấp 2 (Vừa)',
      badgeColor: 'orange',
      description: 'Vi phình mạch vi tuần hoàn kèm rải rác xuất tiết và xuất huyết đốm nhẹ.',
    ),
    _sample(
      'IDRiD_003.jpg',
      name: 'Võng mạc Tiểu đường Tăng sinh (Stage 4)',
      category: 'Đái tháo đường (DR)',
      tag: 'DR Cấp 4 (Tăng sinh)',
      badgeColor: 'red',
      description: 'Hình thành tân mạch võng mạc (Neovascularization), xuất huyết dịch kính nghiêm trọng.',
    ),
    _sample(
      'IDRiD_004.jpg',
      name: 'Võng mạc Tiểu đường Nhẹ (Stage 1)',
      category: 'Đái tháo đường (DR)',
      tag: 'DR Cấp 1 (Nhẹ)',
      badgeColor: 'amber',
      description: 'Giai đoạn khởi phát: chỉ xuất hiện các nốt vi phình mạch nhỏ (Microaneurysms) đơn độc.',
    ),
    _sample(
      'IDRiD_005.jpg',
      name: 'Võng mạc Tiểu đường Tiền Tăng sinh',
      category: 'Đái tháo đường (DR)',
      tag: 'DR Nghi ngờ cao',
      badgeColor: 'red',
      description: 'Tổn thương vi mạch tiến triển mạnh, thiếu máu võng mạc diện rộng.',
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

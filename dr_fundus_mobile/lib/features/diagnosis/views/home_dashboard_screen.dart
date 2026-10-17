import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import '../../../core/constants/app_colors.dart';
import '../../history/views/history_screen.dart';
import '../../settings/controllers/settings_controller.dart';
import '../../settings/views/server_settings_screen.dart';
import '../controllers/diagnosis_controller.dart';
import '../widgets/sample_carousel.dart';
import 'result_screen.dart';

class HomeDashboardScreen extends ConsumerWidget {
  const HomeDashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(diagnosisProvider);
    final notifier = ref.read(diagnosisProvider.notifier);
    final settingsState = ref.watch(settingsProvider);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0.5,
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: const [
            Text(
              'RetinaGuard Mobile',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: AppColors.textPrimary,
              ),
            ),
            Text(
              'Sàng lọc & Phân độ Võng mạc Đáy mắt (KLCN HUIT)',
              style: TextStyle(fontSize: 10, color: AppColors.textSecondary),
            ),
          ],
        ),
        actions: [
          // Network Connection Status Pill
          GestureDetector(
            onTap: () {
              Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => const ServerSettingsScreen()),
              );
            },
            child: Container(
              margin: const EdgeInsets.symmetric(vertical: 12, horizontal: 4),
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: settingsState.isHealthy ? AppColors.successLight : AppColors.dangerLight,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                  color: settingsState.isHealthy
                      ? AppColors.success.withOpacity(0.3)
                      : AppColors.danger.withOpacity(0.3),
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    Icons.circle,
                    size: 8,
                    color: settingsState.isHealthy ? AppColors.success : AppColors.danger,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    settingsState.isHealthy
                        ? '${settingsState.latencyMs ?? 0}ms'
                        : 'Mất kết nối',
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                      color: settingsState.isHealthy ? AppColors.success : AppColors.danger,
                    ),
                  ),
                ],
              ),
            ),
          ),

          // History Screen Action
          IconButton(
            icon: const Icon(Icons.history, color: AppColors.textPrimary),
            tooltip: 'Lịch sử ca khám',
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => const HistoryScreen()),
              );
            },
          ),

          // Settings Action
          IconButton(
            icon: const Icon(Icons.settings_outlined, color: AppColors.textPrimary),
            tooltip: 'Cài đặt máy chủ AI',
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => const ServerSettingsScreen()),
              );
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Top System Status Card
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFF0F172A), Color(0xFF1E293B)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(12),
                boxShadow: [
                  BoxShadow(
                    color: AppColors.primary.withOpacity(0.15),
                    blurRadius: 10,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                        decoration: BoxDecoration(
                          color: AppColors.accent.withOpacity(0.3),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: const Text(
                          'HỆ THỐNG 3 MÔ HÌNH HỌC SÂU ĐỘC LẬP',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 9,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      const Text(
                        'FastAPI + LiteRT',
                        style: TextStyle(color: Colors.white54, fontSize: 9),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Sàng lọc Lưu động & Tele-Ophthalmology',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  const Text(
                    'Model A trên máy (τ=0.965) • Model B trên server: ensemble 6 lớp, ResNet 0.25 và ViT 0.75.',
                    style: TextStyle(color: Colors.white70, fontSize: 11, height: 1.3),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Image Picker Section
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppColors.cardBorder),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Nạp ảnh đáy mắt cần chẩn đoán:',
                    style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                  ),
                  const SizedBox(height: 10),

                  // Image Preview Box (If image selected)
                  if (state.imageBytes != null) ...[
                    Stack(
                      children: [
                        ClipRRect(
                          borderRadius: BorderRadius.circular(8),
                          child: Container(
                            height: 200,
                            width: double.infinity,
                            color: Colors.black,
                            child: Image.memory(
                              state.imageBytes!,
                              fit: BoxFit.contain,
                            ),
                          ),
                        ),
                        Positioned(
                          top: 8,
                          right: 8,
                          child: GestureDetector(
                            onTap: notifier.clearImage,
                            child: Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                              decoration: BoxDecoration(
                                color: Colors.black.withOpacity(0.7),
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: Row(
                                children: const [
                                  Icon(Icons.close, size: 14, color: Colors.white),
                                  SizedBox(width: 4),
                                  Text(
                                    'Đổi ảnh khác',
                                    style: TextStyle(color: Colors.white, fontSize: 11),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Tệp: ${state.imageName ?? "fundus_scan.jpg"}',
                      style: const TextStyle(fontSize: 11, color: AppColors.textSecondary),
                    ),
                    const SizedBox(height: 12),
                  ] else ...[
                    // Camera & Gallery Buttons Row
                    Row(
                      children: [
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: () => notifier.pickImage(ImageSource.camera),
                            icon: const Icon(Icons.camera_alt_outlined, color: AppColors.accent),
                            label: const Text(
                              'Chụp Camera\n(Kính soi đáy mắt)',
                              textAlign: TextAlign.center,
                              style: TextStyle(fontSize: 11, color: AppColors.textPrimary),
                            ),
                            style: OutlinedButton.styleFrom(
                              padding: const EdgeInsets.symmetric(vertical: 14),
                              side: const BorderSide(color: AppColors.cardBorder),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                            ),
                          ),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: () => notifier.pickImage(ImageSource.gallery),
                            icon: const Icon(Icons.photo_library_outlined, color: AppColors.accent),
                            label: const Text(
                              'Chọn từ\nThư viện ảnh',
                              textAlign: TextAlign.center,
                              style: TextStyle(fontSize: 11, color: AppColors.textPrimary),
                            ),
                            style: OutlinedButton.styleFrom(
                              padding: const EdgeInsets.symmetric(vertical: 14),
                              side: const BorderSide(color: AppColors.cardBorder),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 14),
                  ],

                  // 10 Clinical Sample Gallery
                  const SampleCarousel(),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Error Message (If any)
            if (state.errorMessage != null) ...[
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: AppColors.dangerLight,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: AppColors.danger.withOpacity(0.3)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.error_outline, color: AppColors.danger, size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        state.errorMessage!,
                        style: const TextStyle(color: AppColors.danger, fontSize: 11),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 14),
            ],

            // Analyze CTA Button
            ElevatedButton(
              onPressed: state.isLoading || state.imageBytes == null
                  ? null
                  : () async {
                      await notifier.runAnalysis();
                      if (ref.read(diagnosisProvider).result != null && context.mounted) {
                        Navigator.of(context).push(
                          MaterialPageRoute(builder: (_) => const ResultScreen()),
                        );
                      }
                    },
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.accent,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 15),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                elevation: 2,
              ),
              child: state.isLoading
                  ? Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const SizedBox(
                          width: 18,
                          height: 18,
                          child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                        ),
                        const SizedBox(width: 10),
                        Text(
                          'Đang chạy Models A + B + C song song (${(state.uploadProgress * 100).toInt()}%)...',
                          style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold),
                        ),
                      ],
                    )
                  : Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: const [
                        Icon(Icons.analytics_outlined, size: 20),
                        SizedBox(width: 8),
                        Text(
                          'Phân tích Toàn diện (Models A + B + C)',
                          style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold),
                        ),
                      ],
                    ),
            ),
          ],
        ),
      ),
    );
  }
}

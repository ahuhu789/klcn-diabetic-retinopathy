import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/constants/api_endpoints.dart';
import '../../../core/constants/app_colors.dart';
import '../controllers/settings_controller.dart';

class ServerSettingsScreen extends ConsumerStatefulWidget {
  const ServerSettingsScreen({super.key});

  @override
  ConsumerState<ServerSettingsScreen> createState() => _ServerSettingsScreenState();
}

class _ServerSettingsScreenState extends ConsumerState<ServerSettingsScreen> {
  late TextEditingController _urlController;

  @override
  void initState() {
    super.initState();
    final currentUrl = ref.read(settingsProvider).baseUrl;
    _urlController = TextEditingController(text: currentUrl);
  }

  @override
  void dispose() {
    _urlController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(settingsProvider);
    final notifier = ref.read(settingsProvider.notifier);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Cài đặt Máy chủ & Kết nối AI', style: TextStyle(fontSize: 16)),
        backgroundColor: Colors.white,
        foregroundColor: AppColors.textPrimary,
        elevation: 0.5,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Status Card
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: state.isHealthy ? AppColors.successLight : AppColors.dangerLight,
                borderRadius: BorderRadius.circular(10),
                border: Border.all(
                  color: state.isHealthy ? AppColors.success.withOpacity(0.3) : AppColors.danger.withOpacity(0.3),
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    state.isHealthy ? Icons.check_circle : Icons.error_outline,
                    color: state.isHealthy ? AppColors.success : AppColors.danger,
                    size: 24,
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          state.isHealthy
                              ? 'ĐÃ KẾT NỐI MÁY CHỦ THÀNH CÔNG'
                              : 'CHƯA KẾT NỐI ĐƯỢC MÁY CHỦ',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                            color: state.isHealthy ? AppColors.success : AppColors.danger,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          state.isHealthy
                              ? 'Độ trễ mạng: ${state.latencyMs ?? 0} ms • Model A và ensemble B đã sẵn sàng'
                              : (state.errorMessage ?? 'Vui lòng kiểm tra lại địa chỉ máy chủ và kết nối mạng.'),
                          style: TextStyle(
                            fontSize: 11,
                            color: state.isHealthy ? const Color(0xFF065F46) : const Color(0xFF991B1B),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // Pre-configured Quick Presets
            const Text(
              'Cấu hình nhanh (Presets):',
              style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
            ),
            const SizedBox(height: 8),

            _buildPresetButton(
              title: '1. Windows / Localhost (mặc định)',
              desc: 'Backend local chạy ensemble 6 lớp: 127.0.0.1:8000',
              url: ApiEndpoints.localhostUrl,
            ),
            const SizedBox(height: 8),

            _buildPresetButton(
              title: '2. Mạng nội bộ Wi-Fi (LAN)',
              desc: 'Điện thoại và máy tính cùng Wi-Fi. Sửa IP cho đúng máy chủ.',
              url: ApiEndpoints.wifiLanUrl,
            ),
            const SizedBox(height: 8),

            _buildPresetButton(
              title: '3. Android Emulator',
              desc: 'Cổng bridge tới localhost của máy tính: 10.0.2.2:8000',
              url: ApiEndpoints.emulatorUrl,
            ),
            const SizedBox(height: 8),

            _buildPresetButton(
              title: '4. Hugging Face Space cũ',
              desc: 'Space này chưa được cập nhật ensemble 6 lớp. Không dùng cho bản này.',
              url: ApiEndpoints.hfCloudUrl,
            ),
            const SizedBox(height: 8),

            _buildPresetButton(
              title: '5. Cloudflare Tunnel cũ',
              desc: 'URL mẫu đã hết hạn. Dán tunnel mới vào ô bên dưới nếu bạn tự mở.',
              url: ApiEndpoints.defaultCloudflareUrl,
            ),
            const SizedBox(height: 20),

            // Custom URL Input Field
            const Text(
              'Địa chỉ máy chủ tùy chỉnh (Base URL):',
              style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
            ),
            const SizedBox(height: 8),

            TextField(
              controller: _urlController,
              decoration: InputDecoration(
                hintText: 'https://... hoặc http://192.168.1.xxx:8000',
                filled: true,
                fillColor: Colors.white,
                contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                  borderSide: const BorderSide(color: AppColors.cardBorder),
                ),
                enabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                  borderSide: const BorderSide(color: AppColors.cardBorder),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                  borderSide: const BorderSide(color: AppColors.accent, width: 1.5),
                ),
              ),
              keyboardType: TextInputType.url,
            ),
            const SizedBox(height: 12),

            // Action Buttons (Save & Ping)
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: state.isPinging
                        ? null
                        : () async {
                            await notifier.updateBaseUrl(_urlController.text);
                          },
                    icon: state.isPinging
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                          )
                        : const Icon(Icons.network_check, size: 18),
                    label: Text(state.isPinging ? 'Đang kiểm tra...' : 'Lưu & Kiểm tra kết nối'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.accent,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // Model Information Card
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: AppColors.cardBorder),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Hai mô hình đang dùng:',
                      style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                  const SizedBox(height: 6),
                  _buildModelStatusRow('Model A - MobileNetV3 Gate:', 'Ngưỡng an toàn τ = 0.965, chạy trên máy'),
                  _buildModelStatusRow('Model B - Ensemble 6 lớp:', 'ViT 0.45 / EffB4 0.40 / EffB4 hai đầu ra 0.15, chạy trên server'),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPresetButton({
    required String title,
    required String desc,
    required String url,
  }) {
    final currentUrl = ref.watch(settingsProvider).baseUrl;
    final isSelected = currentUrl == url;

    return GestureDetector(
      onTap: () {
        _urlController.text = url;
        ref.read(settingsProvider.notifier).updateBaseUrl(url);
      },
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: isSelected ? AppColors.accent : AppColors.cardBorder,
            width: isSelected ? 1.5 : 1.0,
          ),
        ),
        child: Row(
          children: [
            Icon(
              isSelected ? Icons.radio_button_checked : Icons.radio_button_off,
              color: isSelected ? AppColors.accent : AppColors.textSecondary,
              size: 18,
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 11)),
                  const SizedBox(height: 2),
                  Text(desc, style: const TextStyle(fontSize: 10, color: AppColors.textSecondary)),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildModelStatusRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontSize: 11, color: AppColors.textSecondary)),
          Text(value, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }
}

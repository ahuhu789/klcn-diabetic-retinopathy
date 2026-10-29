import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/constants/app_colors.dart';
import '../../../core/constants/clinical_constants.dart';
import '../../../core/utils/pdf_report_generator.dart';
import '../controllers/diagnosis_controller.dart';
import '../widgets/model_a_gate_badge.dart';
import '../widgets/dr_stage_card.dart';
import '../widgets/dual_gradcam_viewer.dart';
import '../../../models/prediction_response.dart';
import '../../../core/services/lite_inference_service.dart';

class ResultScreen extends ConsumerWidget {
  const ResultScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(diagnosisProvider);
    final notifier = ref.read(diagnosisProvider.notifier);

    final res = state.result;
    if (res == null) {
      return const Center(child: Text('Chưa có kết quả phân tích.'));
    }

    final isRejected = !res.isFundus || res.fundusConfidence < res.threshold;

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Báo cáo Chẩn đoán AI', style: TextStyle(fontSize: 16)),
        backgroundColor: Colors.white,
        foregroundColor: AppColors.textPrimary,
        elevation: 0.5,
        actions: [
          if (!isRejected)
            IconButton(
              icon: const Icon(Icons.picture_as_pdf, color: AppColors.accent),
              tooltip: 'Xuất Phiếu Kết Quả PDF',
              onPressed: () {
                PdfReportGenerator.generateAndShare(
                  patientName: state.selectedSample != null
                      ? '[Ảnh mẫu] ${state.selectedSample!.name}'
                      : 'Bệnh nhân khám ngoại trú',
                  patientId: 'BN-${DateTime.now().millisecondsSinceEpoch.toString().substring(7)}',
                  timestamp: DateTime.now(),
                  result: res,
                  originalImageBytes: state.imageBytes,
                );
              },
            ),
        ],
      ),
      body: Column(
        children: [
          // Sub-header: Latency & Gate summary
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            color: Colors.white,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    const Icon(Icons.speed, size: 16, color: AppColors.textSecondary),
                    const SizedBox(width: 4),
                    Text(
                      'Thời gian xử lý: ${res.processingTimeMs?.toStringAsFixed(0) ?? "2400"} ms',
                      style: const TextStyle(fontSize: 11, color: AppColors.textSecondary),
                    ),
                  ],
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: isRejected ? AppColors.dangerLight : AppColors.successLight,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    isRejected ? 'Model A: Chặn an toàn' : 'Model A: Vượt qua',
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                      color: isRejected ? AppColors.danger : AppColors.success,
                    ),
                  ),
                ),
              ],
            ),
          ),

          // If rejected by Model A: show safety warning and stop
          if (isRejected)
            Expanded(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    ModelAGateBadge(
                      isFundus: res.isFundus,
                      confidence: res.fundusConfidence,
                      threshold: res.threshold,
                    ),
                    const SizedBox(height: 20),
                    const Text(
                      'Cơ chế bảo vệ Fail-Safe đã kích hoạt:',
                      style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                    ),
                    const SizedBox(height: 6),
                    const Text(
                      'Ảnh có độ tin cậy thấp hơn ngưỡng 0.965. Model B không được chạy.',
                      style: TextStyle(fontSize: 12, color: AppColors.textSecondary, height: 1.4),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
            )
          else ...[
            // 4 Navigation Tabs
            Container(
              color: Colors.white,
              child: SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
                child: Row(
                  children: [
                    _buildTabButton(0, 'Tổng quan', Icons.dashboard_outlined, state.dashboardTab, notifier),
                    const SizedBox(width: 6),
                    _buildTabButton(1, 'Model B: 6 lớp', Icons.remove_red_eye_outlined, state.dashboardTab, notifier),
                    const SizedBox(width: 6),
                    _buildTabButton(2, 'Giải thích', Icons.info_outline, state.dashboardTab, notifier),
                  ],
                ),
              ),
            ),
            const Divider(height: 1, color: AppColors.cardBorder),

            // Tab Content
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(14),
                child: _buildTabContent(state.dashboardTab, res, state),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildTabButton(int index, String title, IconData icon, int currentTab, DiagnosisNotifier notifier) {
    final isSelected = currentTab == index;
    return GestureDetector(
      behavior: HitTestBehavior.opaque,
      onTap: () => notifier.setDashboardTab(index),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
        decoration: BoxDecoration(
          color: isSelected ? AppColors.accent : AppColors.background,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isSelected ? AppColors.accent : AppColors.cardBorder,
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              icon,
              size: 14,
              color: isSelected ? Colors.white : AppColors.textSecondary,
            ),
            const SizedBox(width: 5),
            Text(
              title,
              style: TextStyle(
                fontSize: 11,
                fontWeight: isSelected ? FontWeight.bold : FontWeight.w600,
                color: isSelected ? Colors.white : AppColors.textSecondary,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _liteNote() {
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: const Color(0xFFF0F9FF),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: const Color(0xFFBAE6FD)),
      ),
      child: const Text(
        'Kết quả từ mô hình Lite (offline). ${LiteInferenceService.testNote}',
        style: TextStyle(fontSize: 11, height: 1.4, color: Color(0xFF075985)),
      ),
    );
  }

  Widget _litePreprocessed(DiagnosisState state) {
    Widget box(String title, Uint8List? bytes) => Expanded(
          child: Column(
            children: [
              Text(title, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
              const SizedBox(height: 6),
              if (bytes != null)
                ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: Image.memory(bytes, fit: BoxFit.cover, height: 150),
                ),
            ],
          ),
        );
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.cardBorder),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(children: [
            box('Ảnh gốc', state.imageBytes),
            const SizedBox(width: 10),
            box('Ben Graham 512 (đầu vào Lite)', state.preprocessedBytes),
          ]),
          const SizedBox(height: 8),
          const Text(
            'Chế độ Lite không tính Grad-CAM để giữ nhẹ. Chọn tab API để xem bản đồ nhiệt.',
            style: TextStyle(fontSize: 10.5, color: AppColors.textSecondary),
          ),
        ],
      ),
    );
  }

  Widget _buildTabContent(int tabIndex, PredictionResponse res, DiagnosisState state) {
    switch (tabIndex) {
      case 0:
        // Tab 0: Tổng quan Chẩn đoán
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (state.isLite) _liteNote(),
            ModelAGateBadge(
              isFundus: res.isFundus,
              confidence: res.fundusConfidence,
              threshold: res.threshold,
            ),
            const SizedBox(height: 12),
            if (res.drResult != null)
              DRStageCard(
                drResult: res.drResult!,
                branches: res.branches,
              )
            else if (res.drError != null)
              Text(res.drError!, style: const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
          ],
        );

      case 1:
        // Tab 1: Model B & XAI Grad-CAM
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (res.drResult != null)
              DRStageCard(
                drResult: res.drResult!,
                branches: res.branches,
              ),
            const SizedBox(height: 14),
            if (state.isLite) _litePreprocessed(state) else const DualGradCamViewer(),
          ],
        );

      case 2:
      default:
        // Tab 3: Giải thích kiến trúc & Tuyên bố trách nhiệm y khoa
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (state.isLite) ...[
              _liteNote(),
              const Text(
                'Lite: Model A và student EfficientNet-B4-448 hai đầu ra chạy trên máy (TFLite fp16). Tiền xử lý giống server: Ben Graham 512, JPEG q92, resize 448, chuẩn hóa ImageNet, TTA lật ngang. Giải mã hier_ext: p1 × 1.5 rồi chuẩn hóa; lớp 5 nếu p5 > 0.45, nhưng nếu mức DR cao nhất là 0 thì cần p5 > 0.75. Xác suất hiển thị là xác suất sau khi nhân trọng số lớp 1.',
                style: TextStyle(fontSize: 11, height: 1.4, color: AppColors.textPrimary),
              ),
              const SizedBox(height: 12),
            ],
            // Decoupling Rationale Card
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: AppColors.cardBorder),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: const [
                  Text(
                    'NGUYÊN TẮC THIẾT KẾ DECOUPLED PIPELINE',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: AppColors.accent),
                  ),
                  SizedBox(height: 8),
                  Text(
                    '1. Model A chạy trên điện thoại và chỉ nhận hoặc từ chối ảnh đáy mắt.',
                    style: TextStyle(fontSize: 11, height: 1.4, color: AppColors.textPrimary),
                  ),
                  SizedBox(height: 6),
                  Text(
                    '2. Model B chạy trên server: Ben Graham 512, rồi ensemble ViT-B/16-384 (0.45), EfficientNet-B4-448 (0.40) và EfficientNet-B4 hai đầu ra (0.15). Lớp 0–4 là DR. Lớp 5 là nhóm không phải DR.',
                    style: TextStyle(fontSize: 11, height: 1.4, color: AppColors.textPrimary),
                  ),
                  SizedBox(height: 6),
                  Text(
                    '3. Giải mã phân tầng khóa trên validation: nếu p(lớp 5) > 0.50 thì kết quả là lớp 5, nếu không lấy argmax của lớp 0–4. TEST: SCORE 0.6861, QWK_DR 0.7572, macro-F1 0.6151. Lớp 5 không nêu tên từng bệnh.',
                    style: TextStyle(fontSize: 11, height: 1.4, color: AppColors.textSecondary),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 14),

            // Clinical Disclaimer
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: AppColors.warningLight.withOpacity(0.5),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: AppColors.warning.withOpacity(0.3)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: const [
                  Row(
                    children: [
                      Icon(Icons.shield_outlined, size: 18, color: AppColors.warning),
                      SizedBox(width: 6),
                      Text(
                        'TUYÊN BỐ MIỄN TRỪ TRÁCH NHIỆM Y KHOA',
                        style: TextStyle(fontWeight: FontWeight.bold, fontSize: 11, color: AppColors.warning),
                      ),
                    ],
                  ),
                  SizedBox(height: 8),
                  Text(
                    ClinicalConstants.clinicalDisclaimer,
                    style: TextStyle(fontSize: 11, height: 1.4, color: AppColors.textPrimary),
                  ),
                ],
              ),
            ),
          ],
        );
    }
  }
}

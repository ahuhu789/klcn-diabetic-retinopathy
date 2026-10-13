import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/constants/app_colors.dart';
import '../../../core/constants/clinical_constants.dart';
import '../../../core/utils/pdf_report_generator.dart';
import '../controllers/diagnosis_controller.dart';
import '../widgets/model_a_gate_badge.dart';
import '../widgets/dr_stage_card.dart';
import '../widgets/model_c_matrix_table.dart';
import '../widgets/dual_gradcam_viewer.dart';
import '../../../models/prediction_response.dart';

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
                      'Hình ảnh nạp vào có độ tin cậy thấp hơn ngưỡng an toàn nghiêm ngặt 0.965. Để tránh sinh ra chẩn đoán giả, hệ thống tự động ngắt Model B và Model C.',
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
                    _buildTabButton(1, 'Model B: DR & XAI', Icons.remove_red_eye_outlined, state.dashboardTab, notifier),
                    const SizedBox(width: 6),
                    _buildTabButton(2, 'Model C: Sàng lọc', Icons.medical_services_outlined, state.dashboardTab, notifier),
                    const SizedBox(width: 6),
                    _buildTabButton(3, 'Giải thích & Disclaimer', Icons.info_outline, state.dashboardTab, notifier),
                  ],
                ),
              ),
            ),
            const Divider(height: 1, color: AppColors.cardBorder),

            // Tab Content
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(14),
                child: _buildTabContent(state.dashboardTab, res),
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

  Widget _buildTabContent(int tabIndex, PredictionResponse res) {
    switch (tabIndex) {
      case 0:
        // Tab 0: Tổng quan Chẩn đoán
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            ModelAGateBadge(
              isFundus: res.isFundus,
              confidence: res.fundusConfidence,
              threshold: res.threshold,
            ),
            const SizedBox(height: 12),
            if (res.drResult != null)
              DRStageCard(
                drResult: res.drResult!,
                drResnet: res.drResnet,
                drVit: res.drVit,
              ),
            const SizedBox(height: 12),
            if (res.modelCResult != null)
              ModelCMatrixTable(modelCResult: res.modelCResult!),
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
                drResnet: res.drResnet,
                drVit: res.drVit,
              ),
            const SizedBox(height: 14),
            const DualGradCamViewer(),
          ],
        );

      case 2:
        // Tab 2: Model C Sàng lọc Đa bệnh lý
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (res.modelCResult != null)
              ModelCMatrixTable(modelCResult: res.modelCResult!),
          ],
        );

      case 3:
      default:
        // Tab 3: Giải thích kiến trúc & Tuyên bố trách nhiệm y khoa
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
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
                    '1. Model B giải bài toán Ordinal Staging (Xếp hạng thứ tự 5 cấp độ nghiêm trọng) chuyên biệt cho riêng bệnh nhân đái tháo đường.',
                    style: TextStyle(fontSize: 11, height: 1.4, color: AppColors.textPrimary),
                  ),
                  SizedBox(height: 6),
                  Text(
                    '2. Model C giải bài toán Multi-label Screening (Sàng lọc nhị phân đa bệnh lý) trên tập dữ liệu tổng hợp RFMiD + ODIR-5K.',
                    style: TextStyle(fontSize: 11, height: 1.4, color: AppColors.textPrimary),
                  ),
                  SizedBox(height: 6),
                  Text(
                    '3. Hai mô hình hoạt động trên 2 không gian bài toán toán học khác nhau. Việc tách biệt luồng xử lý đảm bảo sự cố của một mô hình không làm sập toàn bộ hệ thống và kết quả của hai mô hình không can thiệp, không làm sai lệch tính liêm chính khoa học của nhau.',
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

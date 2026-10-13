import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/constants/app_colors.dart';
import '../../../core/utils/pdf_report_generator.dart';
import '../controllers/history_controller.dart';

class HistoryScreen extends ConsumerWidget {
  const HistoryScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final history = ref.watch(historyProvider);
    final notifier = ref.read(historyProvider.notifier);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Lịch sử Ca Khám Sàng lọc', style: TextStyle(fontSize: 16)),
        backgroundColor: Colors.white,
        foregroundColor: AppColors.textPrimary,
        elevation: 0.5,
        actions: [
          if (history.isNotEmpty)
            IconButton(
              icon: const Icon(Icons.delete_sweep, size: 20, color: AppColors.danger),
              tooltip: 'Xóa toàn bộ lịch sử',
              onPressed: () {
                showDialog(
                  context: context,
                  builder: (ctx) => AlertDialog(
                    title: const Text('Xác nhận xóa', style: TextStyle(fontSize: 15)),
                    content: const Text('Bạn có chắc chắn muốn xóa toàn bộ lịch sử các ca khám không?'),
                    actions: [
                      TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Hủy')),
                      TextButton(
                        onPressed: () {
                          notifier.clearAll();
                          Navigator.pop(ctx);
                        },
                        child: const Text('Xóa hết', style: TextStyle(color: AppColors.danger)),
                      ),
                    ],
                  ),
                );
              },
            ),
        ],
      ),
      body: history.isEmpty
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: const [
                  Icon(Icons.history, size: 48, color: AppColors.textMuted),
                  SizedBox(height: 12),
                  Text(
                    'Chưa có dữ liệu ca khám nào được lưu.',
                    style: TextStyle(fontSize: 13, color: AppColors.textSecondary),
                  ),
                  SizedBox(height: 4),
                  Text(
                    'Sau khi phân tích ảnh đáy mắt, kết quả sẽ tự động lưu vào đây.',
                    style: TextStyle(fontSize: 11, color: AppColors.textMuted),
                  ),
                ],
              ),
            )
          : ListView.separated(
              padding: const EdgeInsets.all(14),
              itemCount: history.length,
              separatorBuilder: (_, __) => const SizedBox(height: 10),
              itemBuilder: (context, index) {
                final item = history[index];
                final res = item.response;
                final dr = res.drResult;
                final stageColor = dr != null ? AppColors.getStageColor(dr.stage) : AppColors.textSecondary;

                return Dismissible(
                  key: Key(item.id),
                  direction: DismissDirection.endToStart,
                  background: Container(
                    alignment: Alignment.centerRight,
                    padding: const EdgeInsets.only(right: 20),
                    decoration: BoxDecoration(
                      color: AppColors.danger,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: const Icon(Icons.delete, color: Colors.white),
                  ),
                  onDismissed: (_) => notifier.deleteRecord(item.id),
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: AppColors.cardBorder),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.03),
                          blurRadius: 4,
                          offset: const Offset(0, 2),
                        ),
                      ],
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Row 1: Patient Name & Timestamp
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              item.patientName,
                              style: const TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.bold,
                                color: AppColors.textPrimary,
                              ),
                            ),
                            Text(
                              item.timestamp.toString().substring(0, 16),
                              style: const TextStyle(fontSize: 11, color: AppColors.textSecondary),
                            ),
                          ],
                        ),
                        const SizedBox(height: 6),

                        // Row 2: Model A & Model B & Model C Status Pills
                        Wrap(
                          spacing: 6,
                          runSpacing: 4,
                          children: [
                            // Model A Pill
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                              decoration: BoxDecoration(
                                color: res.isFundus ? AppColors.successLight : AppColors.dangerLight,
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: Text(
                                res.isFundus ? 'Gate: Hợp lệ' : 'Gate: Từ chối',
                                style: TextStyle(
                                  fontSize: 10,
                                  fontWeight: FontWeight.bold,
                                  color: res.isFundus ? AppColors.success : AppColors.danger,
                                ),
                              ),
                            ),

                            // Model B DR Stage Pill
                            if (dr != null)
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                decoration: BoxDecoration(
                                  color: stageColor.withOpacity(0.12),
                                  borderRadius: BorderRadius.circular(4),
                                ),
                                child: Text(
                                  'DR Cấp ${dr.stage} (${(dr.confidence * 100).toStringAsFixed(0)}%)',
                                  style: TextStyle(
                                    fontSize: 10,
                                    fontWeight: FontWeight.bold,
                                    color: stageColor,
                                  ),
                                ),
                              ),

                            // Model C Risk Pill
                            if (res.modelCResult != null)
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                decoration: BoxDecoration(
                                  color: res.modelCResult!.overallDiseaseRisk
                                      ? AppColors.dangerLight
                                      : AppColors.successLight,
                                  borderRadius: BorderRadius.circular(4),
                                ),
                                child: Text(
                                  res.modelCResult!.overallDiseaseRisk
                                      ? 'Phát hiện ${res.modelCResult!.numDetectedConditions} bệnh'
                                      : 'Võng mạc bình thường',
                                  style: TextStyle(
                                    fontSize: 10,
                                    fontWeight: FontWeight.bold,
                                    color: res.modelCResult!.overallDiseaseRisk
                                        ? AppColors.danger
                                        : AppColors.success,
                                  ),
                                ),
                              ),
                          ],
                        ),
                        const SizedBox(height: 8),

                        // Actions Row: Export PDF
                        Row(
                          mainAxisAlignment: MainAxisAlignment.end,
                          children: [
                            TextButton.icon(
                              onPressed: () {
                                PdfReportGenerator.generateAndShare(
                                  patientName: item.patientName,
                                  patientId: item.patientId,
                                  timestamp: item.timestamp,
                                  result: res,
                                );
                              },
                              icon: const Icon(Icons.picture_as_pdf, size: 16, color: AppColors.accent),
                              label: const Text('Xuất PDF', style: TextStyle(fontSize: 11, color: AppColors.accent)),
                              style: TextButton.styleFrom(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                visualDensity: VisualDensity.compact,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
    );
  }
}

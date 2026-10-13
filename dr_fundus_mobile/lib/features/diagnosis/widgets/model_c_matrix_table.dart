import 'package:flutter/material.dart';
import '../../../core/constants/app_colors.dart';
import '../../../models/model_c_prediction.dart';

class ModelCMatrixTable extends StatelessWidget {
  final ModelCPrediction modelCResult;

  const ModelCMatrixTable({
    super.key,
    required this.modelCResult,
  });

  @override
  Widget build(BuildContext context) {
    final hasRisk = modelCResult.overallDiseaseRisk;

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.cardBorder),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Overall Risk Banner
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: hasRisk ? AppColors.dangerLight : AppColors.successLight,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(
                color: hasRisk ? AppColors.danger.withOpacity(0.3) : AppColors.success.withOpacity(0.3),
              ),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(
                  hasRisk ? Icons.warning_rounded : Icons.check_circle_rounded,
                  color: hasRisk ? AppColors.danger : AppColors.success,
                  size: 20,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        hasRisk
                            ? 'CẢNH BÁO: PHÁT HIỆN DẤU HIỆU BỆNH LÝ TRÊN VÕNG MẠC'
                            : 'BÌNH THƯỜNG: CHƯA PHÁT HIỆN TỔN THƯƠNG RÕ RỆT',
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                          color: hasRisk ? AppColors.danger : AppColors.success,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        'Tín hiệu rủi ro chung (Disease Risk flag) từ tập dữ liệu RFMiD; phản ánh sự hiện diện của ít nhất một tổn thương võng mạc.',
                        style: TextStyle(
                          fontSize: 10,
                          color: hasRisk ? const Color(0xFF991B1B) : const Color(0xFF065F46),
                          height: 1.3,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),

          // Detected Diseases Chips
          if (modelCResult.detectedDiseases.isNotEmpty) ...[
            const Text(
              'Các bệnh lý phát hiện vượt ngưỡng (τ):',
              style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppColors.textSecondary),
            ),
            const SizedBox(height: 6),
            Wrap(
              spacing: 6,
              runSpacing: 6,
              children: modelCResult.detectedDiseases.map((disease) {
                return Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: AppColors.dangerLight,
                    borderRadius: BorderRadius.circular(6),
                    border: Border.all(color: AppColors.danger.withOpacity(0.3)),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.circle, size: 6, color: AppColors.danger),
                      const SizedBox(width: 5),
                      Text(
                        '${disease.name} (${disease.confidencePct.toStringAsFixed(1)}%)',
                        style: const TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                          color: AppColors.danger,
                        ),
                      ),
                    ],
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: 12),
          ],

          // 10 Conditions Table
          const Text(
            'Ma trận sàng lọc 10 bệnh lý võng mạc (Model C E2):',
            style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppColors.textSecondary),
          ),
          const SizedBox(height: 8),

          ...modelCResult.fullProbabilities.entries.map((entry) {
            final k = entry.key;
            final v = entry.value as Map<String, dynamic>;
            final name = v['name'] ?? k;
            final prob = (v['probability'] as num?)?.toDouble() ?? 0.0;
            final thresh = (v['threshold'] as num?)?.toDouble() ?? 0.5;
            final isDetected = v['detected'] == true;

            return Container(
              margin: const EdgeInsets.only(bottom: 8),
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: isDetected ? AppColors.dangerLight.withOpacity(0.4) : AppColors.background,
                borderRadius: BorderRadius.circular(6),
                border: Border.all(
                  color: isDetected ? AppColors.danger.withOpacity(0.3) : AppColors.cardBorder,
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Text(
                          '$name ($k)',
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: isDetected ? FontWeight.bold : FontWeight.w600,
                            color: isDetected ? AppColors.danger : AppColors.textPrimary,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: isDetected ? AppColors.danger : Colors.grey.shade300,
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(
                          isDetected ? 'DƯƠNG TÍNH' : 'ÂM TÍNH',
                          style: TextStyle(
                            fontSize: 9,
                            fontWeight: FontWeight.bold,
                            color: isDetected ? Colors.white : Colors.grey.shade700,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Row(
                    children: [
                      Expanded(
                        child: Stack(
                          children: [
                            ClipRRect(
                              borderRadius: BorderRadius.circular(4),
                              child: LinearProgressIndicator(
                                value: prob.clamp(0.0, 1.0),
                                minHeight: 7,
                                backgroundColor: Colors.grey.shade200,
                                valueColor: AlwaysStoppedAnimation<Color>(
                                  isDetected ? AppColors.danger : AppColors.accent,
                                ),
                              ),
                            ),
                            // Vạch chỉ báo ngưỡng quyết định threshold
                            Positioned(
                              left: 0,
                              right: 0,
                              top: 0,
                              bottom: 0,
                              child: LayoutBuilder(
                                builder: (ctx, constraints) {
                                  final double offset = constraints.maxWidth * thresh.clamp(0.0, 1.0);
                                  return Stack(
                                    children: [
                                      Positioned(
                                        left: offset - 1,
                                        top: 0,
                                        bottom: 0,
                                        child: Container(
                                          width: 2,
                                          color: Colors.black87,
                                        ),
                                      ),
                                    ],
                                  );
                                },
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        '${(prob * 100).toStringAsFixed(1)}% (τ: ${(thresh * 100).toStringAsFixed(0)}%)',
                        style: TextStyle(
                          fontSize: 10,
                          fontWeight: FontWeight.w600,
                          color: isDetected ? AppColors.danger : AppColors.textSecondary,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            );
          }),
        ],
      ),
    );
  }
}

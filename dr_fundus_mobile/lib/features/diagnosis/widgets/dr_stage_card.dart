import 'package:flutter/material.dart';
import '../../../core/constants/app_colors.dart';
import '../../../models/dr_prediction.dart';

class DRStageCard extends StatelessWidget {
  final DRPrediction drResult;
  final DRPrediction? drResnet;
  final DRPrediction? drVit;

  const DRStageCard({
    super.key,
    required this.drResult,
    this.drResnet,
    this.drVit,
  });

  @override
  Widget build(BuildContext context) {
    final stageColor = AppColors.getStageColor(drResult.stage);
    final hasAgreement = drVit != null && drResnet != null && drVit!.stage == drResnet!.stage;

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
          // Header Row with Stage Badge & Agreement Tag
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Flexible(
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: stageColor.withOpacity(0.12),
                    borderRadius: BorderRadius.circular(6),
                    border: Border.all(color: stageColor.withOpacity(0.3)),
                  ),
                  child: Text(
                    'CẤP ĐỘ ${drResult.stage}: ${drResult.badge.toUpperCase()}',
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: stageColor,
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 8),
              if (drVit != null && drResnet != null)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: hasAgreement ? AppColors.successLight : AppColors.warningLight,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    hasAgreement ? 'Đồng thuận ViT & CNN' : 'Chênh lệch ViT & CNN',
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w600,
                      color: hasAgreement ? AppColors.success : AppColors.warning,
                    ),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 10),

          // Confidence & Description
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Độ tin cậy phân loại:',
                style: TextStyle(fontSize: 12, color: AppColors.textSecondary),
              ),
              Text(
                '${(drResult.confidence * 100).toStringAsFixed(1)}%',
                style: const TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.bold,
                  color: AppColors.textPrimary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            drResult.description,
            style: const TextStyle(
              fontSize: 12,
              color: AppColors.textPrimary,
              height: 1.35,
            ),
          ),
          const SizedBox(height: 8),

          // Clinical Advice Box
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: AppColors.background,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: AppColors.cardBorder),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.medical_services_outlined, size: 16, color: AppColors.accent),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Lời khuyên lâm sàng: ${drResult.advice}',
                    style: const TextStyle(
                      fontSize: 11,
                      color: AppColors.textSecondary,
                      height: 1.35,
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),

          // 5-class Probability Distribution Bars
          const Text(
            'Phân bố xác suất 5 giai đoạn (ICDR 0 - 4):',
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.bold,
              color: AppColors.textSecondary,
            ),
          ),
          const SizedBox(height: 6),
          ...List.generate(5, (stageIdx) {
            final key = stageIdx.toString();
            final prob = drResult.probabilities[key] ?? 0.0;
            final isCurrentStage = drResult.stage == stageIdx;
            final barColor = AppColors.getStageColor(stageIdx);

            return Padding(
              padding: const EdgeInsets.symmetric(vertical: 3),
              child: Row(
                children: [
                  SizedBox(
                    width: 70,
                    child: Text(
                      'Cấp $stageIdx',
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: isCurrentStage ? FontWeight.bold : FontWeight.normal,
                        color: isCurrentStage ? barColor : AppColors.textSecondary,
                      ),
                    ),
                  ),
                  Expanded(
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(4),
                      child: LinearProgressIndicator(
                        value: prob,
                        minHeight: 8,
                        backgroundColor: AppColors.cardBorder,
                        valueColor: AlwaysStoppedAnimation<Color>(barColor),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  SizedBox(
                    width: 45,
                    child: Text(
                      '${(prob * 100).toStringAsFixed(1)}%',
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: isCurrentStage ? FontWeight.bold : FontWeight.normal,
                        color: isCurrentStage ? barColor : AppColors.textSecondary,
                      ),
                      textAlign: TextAlign.right,
                    ),
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

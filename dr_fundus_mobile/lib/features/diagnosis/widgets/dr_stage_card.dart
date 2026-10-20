import 'package:flutter/material.dart';
import '../../../core/constants/app_colors.dart';
import '../../../core/constants/clinical_constants.dart';
import '../../../models/dr_prediction.dart';

class DRStageCard extends StatelessWidget {
  final DRPrediction drResult;

  /// Các nhánh của ensemble Model B v3 (ViT-B/16-384, EffB4-448, EffB4 hai đầu ra).
  final List<DRPrediction> branches;

  const DRStageCard({
    super.key,
    required this.drResult,
    this.branches = const [],
  });

  @override
  Widget build(BuildContext context) {
    final stageColor = AppColors.getStageColor(drResult.stage);
    final hasAgreement = branches.isNotEmpty && branches.every((b) => b.stage == drResult.stage);

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
                    drResult.stage == 5
                        ? 'LỚP 5: ${drResult.badge.toUpperCase()}'
                        : 'CẤP ${drResult.stage}: ${drResult.badge.toUpperCase()}',
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
              if (branches.length > 1)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: hasAgreement ? AppColors.successLight : AppColors.warningLight,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    hasAgreement
                        ? 'Đồng thuận ${branches.length} nhánh'
                        : 'Các nhánh chênh lệch',
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

          if (branches.isNotEmpty) ...[
            Wrap(
              spacing: 6,
              runSpacing: 4,
              children: branches.map((b) {
                final label = ClinicalConstants.branchLabels[b.branch] ?? b.modelUsed;
                final w = b.weight != null ? ' • ${b.weight!.toStringAsFixed(2)}' : '';
                return Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: AppColors.background,
                    borderRadius: BorderRadius.circular(4),
                    border: Border.all(color: AppColors.cardBorder),
                  ),
                  child: Text(
                    '$label$w: lớp ${b.stage}',
                    style: const TextStyle(fontSize: 10, color: AppColors.textSecondary),
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: 10),
          ],

          // 6-class Probability Distribution Bars
          const Text(
            'Phân bố xác suất 6 lớp (DR 0 - 4 và lớp 5):',
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.bold,
              color: AppColors.textSecondary,
            ),
          ),
          const SizedBox(height: 6),
          ...List.generate(6, (stageIdx) {
            final prob = drResult.probFor(stageIdx);
            final isCurrentStage = drResult.stage == stageIdx;
            final barColor = AppColors.getStageColor(stageIdx);

            return Padding(
              padding: const EdgeInsets.symmetric(vertical: 3),
              child: Row(
                children: [
                  SizedBox(
                    width: 70,
                    child: Text(
                      stageIdx == 5 ? 'Lớp 5' : 'Cấp $stageIdx',
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

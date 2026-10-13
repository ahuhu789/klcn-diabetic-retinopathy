import 'package:flutter/material.dart';
import '../../../core/constants/app_colors.dart';

class ModelAGateBadge extends StatelessWidget {
  final bool isFundus;
  final double confidence;
  final double threshold;

  const ModelAGateBadge({
    super.key,
    required this.isFundus,
    required this.confidence,
    this.threshold = 0.965,
  });

  @override
  Widget build(BuildContext context) {
    final bool passed = isFundus && confidence >= threshold;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: passed ? AppColors.successLight : AppColors.dangerLight,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: passed ? AppColors.success.withOpacity(0.3) : AppColors.danger.withOpacity(0.3),
        ),
      ),
      child: Row(
        children: [
          Icon(
            passed ? Icons.check_circle : Icons.warning_amber_rounded,
            color: passed ? AppColors.success : AppColors.danger,
            size: 20,
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  passed
                      ? 'MODEL A (FUNDUS GATE): HỢP LỆ'
                      : 'MODEL A (FUNDUS GATE): TỪ CHỐI AN TOÀN',
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                    color: passed ? AppColors.success : AppColors.danger,
                  ),
                ),
                const SizedBox(height: 1),
                Text(
                  passed
                      ? 'Ảnh đạt chuẩn đáy võng mạc (Độ tin cậy: ${(confidence * 100).toStringAsFixed(1)}% ≥ ${(threshold * 100).toStringAsFixed(1)}%)'
                      : 'Không phải ảnh đáy mắt hợp lệ (Độ tin cậy: ${(confidence * 100).toStringAsFixed(1)}% < ${(threshold * 100).toStringAsFixed(1)}%). Pipeline đã dừng an toàn.',
                  style: TextStyle(
                    fontSize: 10,
                    color: passed ? const Color(0xFF065F46) : const Color(0xFF991B1B),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

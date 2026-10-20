import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/constants/app_colors.dart';
import '../../../models/sample_image_info.dart';
import '../controllers/diagnosis_controller.dart';

class SampleCarousel extends ConsumerWidget {
  const SampleCarousel({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(diagnosisProvider);
    final notifier = ref.read(diagnosisProvider.notifier);

    if (state.samples.isEmpty) {
      return const SizedBox.shrink();
    }

    final filteredSamples = state.samples.where((s) {
      if (state.sampleFilter == 'all') return true;
      return s.category == state.sampleFilter;
    }).toList();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Header
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              children: [
                const Icon(Icons.layers_outlined, size: 18, color: AppColors.accent),
                const SizedBox(width: 6),
                const Text(
                  'Bộ sưu tập 10 ảnh mẫu lâm sàng',
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.bold,
                    color: AppColors.textPrimary,
                  ),
                ),
              ],
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                color: AppColors.accentLight,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                '${filteredSamples.length} mẫu',
                style: const TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                  color: AppColors.accent,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),

        // Category Filter Chips
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            children: [
              _buildFilterChip(
                  context, ref, 'all', 'Tất cả (${state.samples.length})', state.sampleFilter),
              const SizedBox(width: 6),
              _buildFilterChip(
                  context, ref, 'Bệnh võng mạc khác', 'Bệnh khác (AMD, Glaucoma, MYA, BRVO)', state.sampleFilter),
              const SizedBox(width: 6),
              _buildFilterChip(
                  context, ref, 'Đái tháo đường (DR)', 'Tiểu đường (DR 1-4)', state.sampleFilter),
              const SizedBox(width: 6),
              _buildFilterChip(context, ref, 'Khỏe mạnh', 'Khỏe mạnh', state.sampleFilter),
            ],
          ),
        ),
        const SizedBox(height: 10),

        // Horizontal Carousel of Sample Cards
        SizedBox(
          height: 125,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            itemCount: filteredSamples.length,
            separatorBuilder: (_, __) => const SizedBox(width: 8),
            itemBuilder: (context, index) {
              final sample = filteredSamples[index];
              final isSelected = state.selectedSample?.id == sample.id;
              final badgeColor = AppColors.getBadgeColor(sample.badgeColor);

              return GestureDetector(
                onTap: () => notifier.selectSample(sample),
                child: Container(
                  width: 105,
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(
                      color: isSelected ? AppColors.accent : AppColors.cardBorder,
                      width: isSelected ? 2.0 : 1.0,
                    ),
                    boxShadow: isSelected
                        ? [
                            BoxShadow(
                              color: AppColors.accent.withOpacity(0.25),
                              blurRadius: 8,
                              offset: const Offset(0, 2),
                            )
                          ]
                        : [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.03),
                              blurRadius: 4,
                              offset: const Offset(0, 2),
                            )
                          ],
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      // Thumbnail with Tag Overlay
                      Expanded(
                        child: Stack(
                          fit: StackFit.expand,
                          children: [
                            ClipRRect(
                              borderRadius: const BorderRadius.vertical(top: Radius.circular(8)),
                              child: sample.isBundledAsset
                                  ? Image.asset(
                                      sample.url,
                                      fit: BoxFit.cover,
                                      errorBuilder: (_, __, ___) => _brokenThumb(),
                                    )
                                  : Image.network(
                                      sample.url,
                                      fit: BoxFit.cover,
                                      errorBuilder: (_, __, ___) => _brokenThumb(),
                                    ),
                            ),
                            if (sample.tag != null)
                              Positioned(
                                bottom: 4,
                                left: 4,
                                right: 4,
                                child: Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: badgeColor.withOpacity(0.9),
                                    borderRadius: BorderRadius.circular(4),
                                  ),
                                  child: Text(
                                    sample.tag!,
                                    style: const TextStyle(
                                      color: Colors.white,
                                      fontSize: 9,
                                      fontWeight: FontWeight.bold,
                                    ),
                                    textAlign: TextAlign.center,
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ),
                              ),
                          ],
                        ),
                      ),
                      // Title
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 4),
                        child: Text(
                          sample.name,
                          style: TextStyle(
                            fontSize: 10,
                            fontWeight: isSelected ? FontWeight.bold : FontWeight.w600,
                            color: isSelected ? AppColors.accent : AppColors.textPrimary,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          textAlign: TextAlign.center,
                        ),
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        ),

        // Active Sample Description Banner
        if (state.selectedSample != null) ...[
          const SizedBox(height: 10),
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: AppColors.accent.withOpacity(0.3)),
              boxShadow: [
                BoxShadow(
                  color: AppColors.accent.withOpacity(0.05),
                  blurRadius: 6,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
                  decoration: BoxDecoration(
                    color: AppColors.getBadgeColor(state.selectedSample!.badgeColor),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    state.selectedSample!.tag ?? 'Mẫu',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        state.selectedSample!.name,
                        style: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                          color: AppColors.textPrimary,
                        ),
                      ),
                      if (state.selectedSample!.description != null) ...[
                        const SizedBox(height: 2),
                        Text(
                          state.selectedSample!.description!,
                          style: const TextStyle(
                            fontSize: 11,
                            color: AppColors.textSecondary,
                            height: 1.3,
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ],
    );
  }

  Widget _brokenThumb() {
    return Container(
      color: AppColors.primary,
      child: const Icon(Icons.broken_image, color: Colors.white54, size: 24),
    );
  }

  Widget _buildFilterChip(
      BuildContext context, WidgetRef ref, String id, String label, String currentFilter) {
    final isSelected = currentFilter == id;
    return GestureDetector(
      onTap: () => ref.read(diagnosisProvider.notifier).setSampleFilter(id),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
        decoration: BoxDecoration(
          color: isSelected ? AppColors.accent : Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: isSelected ? AppColors.accent : AppColors.cardBorder,
          ),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 11,
            fontWeight: isSelected ? FontWeight.bold : FontWeight.w500,
            color: isSelected ? Colors.white : AppColors.textSecondary,
          ),
        ),
      ),
    );
  }
}

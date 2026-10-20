import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:photo_view/photo_view.dart';
import '../../../core/constants/app_colors.dart';
import '../../../core/constants/clinical_constants.dart';
import '../controllers/diagnosis_controller.dart';

class DualGradCamViewer extends ConsumerWidget {
  const DualGradCamViewer({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(diagnosisProvider);
    final notifier = ref.read(diagnosisProvider.notifier);

    final res = state.result;
    if (res == null) return const SizedBox.shrink();

    // Model B v3: heatmap ensemble + một heatmap cho mỗi nhánh.
    final options = <MapEntry<String, String>>[];
    if (res.drResult?.heatmapBase64 != null) {
      options.add(MapEntry('ensemble', res.drResult!.heatmapBase64!));
    }
    for (final b in res.branches) {
      if (b.heatmapBase64 != null) {
        options.add(MapEntry(b.branch ?? (identical(b, res.drResnet) ? 'resnet' : 'vit'), b.heatmapBase64!));
      }
    }
    final active = options.firstWhere(
      (o) => o.key == state.activeGradCamModel,
      orElse: () => options.isNotEmpty ? options.first : const MapEntry('ensemble', ''),
    );
    final activeKey = active.key;
    final activeHeatmapBase64 = active.value.isEmpty ? null : active.value;

    Uint8List? heatmapBytes;
    if (activeHeatmapBase64 != null) {
      try {
        final cleanBase64 = activeHeatmapBase64
            .replaceAll(RegExp(r'^data:image\/[a-zA-Z]+;base64,'), '');
        heatmapBytes = base64Decode(cleanBase64);
      } catch (_) {}
    }

    final origBytes = state.imageBytes;

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
          // Header with Model Toggle
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'GIẢI THÍCH QUYẾT ĐỊNH (XAI GRAD-CAM)',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                  color: AppColors.textPrimary,
                ),
              ),
              IconButton(
                icon: const Icon(Icons.fullscreen, size: 20, color: AppColors.accent),
                onPressed: () {
                  if (origBytes != null) {
                    _openFullscreenViewer(context, origBytes, heatmapBytes, state.blendOpacity);
                  }
                },
                tooltip: 'Xem toàn màn hình & Phóng to',
              ),
            ],
          ),
          const SizedBox(height: 8),

          // Chọn heatmap: ensemble hoặc từng nhánh
          Wrap(
            spacing: 8,
            runSpacing: 6,
            children: options.map((o) {
              final selected = o.key == activeKey;
              final label = ClinicalConstants.branchLabels[o.key] ?? o.key;
              return GestureDetector(
                onTap: () => notifier.setActiveGradCamModel(o.key),
                child: Container(
                  padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 12),
                  decoration: BoxDecoration(
                    color: selected ? AppColors.accent : AppColors.background,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(
                      color: selected ? AppColors.accent : AppColors.cardBorder,
                    ),
                  ),
                  child: Text(
                    label,
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: selected ? FontWeight.bold : FontWeight.w600,
                      color: selected ? Colors.white : AppColors.textSecondary,
                    ),
                  ),
                ),
              );
            }).toList(),
          ),
          const SizedBox(height: 12),

          // Interactive Blend Canvas
          ClipRRect(
            borderRadius: BorderRadius.circular(10),
            child: Container(
              height: 260,
              width: double.infinity,
              color: AppColors.primary,
              child: Stack(
                fit: StackFit.expand,
                children: [
                  // Original Image Base
                  if (origBytes != null)
                    Image.memory(
                      origBytes,
                      fit: BoxFit.contain,
                    ),

                  // Grad-CAM Heatmap with Opacity Blend
                  if (heatmapBytes != null)
                    Opacity(
                      opacity: state.blendOpacity,
                      child: Image.memory(
                        heatmapBytes,
                        fit: BoxFit.contain,
                      ),
                    ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 10),

          // Opacity Slider
          Row(
            children: [
              const Icon(Icons.opacity, size: 16, color: AppColors.textSecondary),
              const SizedBox(width: 6),
              Text(
                'Độ phủ Heatmap: ${(state.blendOpacity * 100).toInt()}%',
                style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: AppColors.textSecondary),
              ),
              Expanded(
                child: Slider(
                  value: state.blendOpacity,
                  min: 0.0,
                  max: 1.0,
                  divisions: 20,
                  activeColor: AppColors.accent,
                  onChanged: (val) => notifier.setBlendOpacity(val),
                ),
              ),
            ],
          ),

          // Scientific Rationale Note
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: AppColors.background,
              borderRadius: BorderRadius.circular(6),
            ),
            child: Text(
              activeKey == 'ensemble'
                  ? 'Heatmap ensemble là tổng có trọng số (0.45 / 0.40 / 0.15) Grad-CAM của ba nhánh, cùng nhắm vào lớp mà ensemble chọn.'
                  : activeKey == 'vit3'
                      ? 'ViT Grad-CAM tính trên token patch (lưới 24×24) của khối Transformer cuối, cho lớp mà ensemble chọn.'
                      : 'EfficientNet-B4 Grad-CAM tính trên lớp tích chập cuối (bn2), cho lớp mà ensemble chọn.',
              style: const TextStyle(fontSize: 10, color: AppColors.textSecondary, height: 1.3),
            ),
          ),
        ],
      ),
    );
  }

  void _openFullscreenViewer(
      BuildContext context, Uint8List origBytes, Uint8List? heatmapBytes, double opacity) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => Scaffold(
          backgroundColor: Colors.black,
          appBar: AppBar(
            backgroundColor: Colors.black,
            iconTheme: const IconThemeData(color: Colors.white),
            title: const Text('Phóng to Bản đồ nhiệt Grad-CAM', style: TextStyle(color: Colors.white, fontSize: 14)),
          ),
          body: Center(
            child: Stack(
              fit: StackFit.expand,
              children: [
                PhotoView(
                  imageProvider: MemoryImage(origBytes),
                  minScale: PhotoViewComputedScale.contained,
                  maxScale: PhotoViewComputedScale.covered * 3.0,
                ),
                if (heatmapBytes != null)
                  IgnorePointer(
                    child: Opacity(
                      opacity: opacity,
                      child: Image.memory(
                        heatmapBytes,
                        fit: BoxFit.contain,
                      ),
                    ),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

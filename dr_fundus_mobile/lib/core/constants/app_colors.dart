import 'package:flutter/material.dart';

class AppColors {
  // Brand & Medical Palette
  static const Color primary = Color(0xFF0F172A);      // Deep Slate / Navy
  static const Color primaryLight = Color(0xFF1E293B);
  static const Color accent = Color(0xFF0284C7);       // Medical Cyan / Blue
  static const Color accentLight = Color(0xFFE0F2FE);

  // Clinical Status Colors
  static const Color success = Color(0xFF059669);      // Emerald (Normal / Safe)
  static const Color successLight = Color(0xFFD1FAE5);

  static const Color warning = Color(0xFFD97706);      // Amber (Mild / Moderate)
  static const Color warningLight = Color(0xFFFEF3C7);

  static const Color danger = Color(0xFFDC2626);       // Red (Severe / PDR / Reject)
  static const Color dangerLight = Color(0xFFFEE2E2);

  static const Color purple = Color(0xFF9333EA);       // Glaucoma / ODC
  static const Color purpleLight = Color(0xFFF3E8FF);

  static const Color rose = Color(0xFFE11D48);         // BRVO
  static const Color roseLight = Color(0xFFFFE4E6);

  // Surfaces & Backgrounds
  static const Color background = Color(0xFFF8FAFC);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color cardBorder = Color(0xFFE2E8F0);

  // Typography
  static const Color textPrimary = Color(0xFF0F172A);
  static const Color textSecondary = Color(0xFF64748B);
  static const Color textMuted = Color(0xFF94A3B8);

  // Helpers
  static Color getStageColor(int stage) {
    switch (stage) {
      case 0:
        return success;
      case 1:
        return const Color(0xFFEAB308); // Yellow
      case 2:
        return const Color(0xFFF97316); // Orange
      case 3:
        return danger;                 // Red
      case 4:
        return const Color(0xFFB91C1C); // Dark Red
      case 5:
        return const Color(0xFF475569);
      default:
        return textSecondary;
    }
  }

  static Color getBadgeColor(String? colorName) {
    switch (colorName?.toLowerCase()) {
      case 'emerald':
        return success;
      case 'amber':
        return warning;
      case 'purple':
        return purple;
      case 'blue':
        return accent;
      case 'rose':
        return rose;
      case 'red':
        return danger;
      case 'orange':
        return const Color(0xFFEA580C);
      default:
        return accent;
    }
  }
}

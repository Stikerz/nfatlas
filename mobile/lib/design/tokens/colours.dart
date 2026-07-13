import 'package:flutter/material.dart';

/// Colour tokens per `_bmad-output/planning-artifacts/design/tokens.md §1`.
/// Semantic names only — no numeric ramps. Hex values are the contract.
class AtlasColors {
  const AtlasColors._();

  // ── Brand ──────────────────────────────────────────────────────────────
  static const Color brandPrimary = Color(0xFF0F1E38); // midnight navy
  static const Color brandAccent = Color(0xFFC9A96A);  // champagne gold

  // ── Text ───────────────────────────────────────────────────────────────
  static const Color textPrimary = Color(0xFF1A1A1A);
  static const Color textSecondary = Color(0xFF5F5A54);
  static const Color textInverted = Color(0xFFFAF7F2);
  static const Color textAccent = Color(0xFFC9A96A);

  // ── Surfaces ───────────────────────────────────────────────────────────
  static const Color surfaceBase = Color(0xFFFAF7F2);
  static const Color surfaceElevated = Color(0xFFF2EDE4);
  static const Color surfaceInverted = Color(0xFF0F1E38);
  static const Color surfaceSubtle = Color(0xFFF7F3EC);

  // ── State ──────────────────────────────────────────────────────────────
  static const Color stateSuccess = Color(0xFF1E5F4C);   // deep emerald
  static const Color stateAttention = Color(0xFFB87728); // muted amber
  static const Color stateDanger = Color(0xFFA94A38);    // muted terracotta
  static const Color stateInfo = brandPrimary;           // no dedicated blue

  // ── Structural ─────────────────────────────────────────────────────────
  static const Color dividerHairline = Color(0xFFE5DFD6);
  static const Color dividerStrong = Color(0xFFC9C3B7);
  static const Color focusRing = brandPrimary;
}

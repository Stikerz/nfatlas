import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// Typography tokens per `_bmad-output/planning-artifacts/design/tokens.md §2`.
///
/// Weight discipline: Fraunces uses only 400/600/700; Inter uses only
/// 400/500/600/700; JetBrains Mono uses only 400. Enforced by not exposing
/// any other constructor style.
class AtlasType {
  const AtlasType._();

  // ── Display (Fraunces) ─────────────────────────────────────────────────
  static TextStyle get displayHero => GoogleFonts.fraunces(
        fontSize: 64,
        height: 1.05,
        fontWeight: FontWeight.w700,
        letterSpacing: -0.64,
      );

  static TextStyle get displaySection => GoogleFonts.fraunces(
        fontSize: 40,
        height: 1.1,
        fontWeight: FontWeight.w600,
        letterSpacing: -0.20,
      );

  static TextStyle get displayDraw => GoogleFonts.fraunces(
        fontSize: 32,
        height: 1.15,
        fontWeight: FontWeight.w600,
      );

  static TextStyle get displayCard => GoogleFonts.fraunces(
        fontSize: 24,
        height: 1.2,
        fontWeight: FontWeight.w600,
      );

  // ── Body (Inter) ───────────────────────────────────────────────────────
  static TextStyle get bodyDefault => GoogleFonts.inter(
        fontSize: 16,
        height: 1.6,
        fontWeight: FontWeight.w400,
      );

  static TextStyle get bodyEmphasis => GoogleFonts.inter(
        fontSize: 16,
        height: 1.6,
        fontWeight: FontWeight.w600,
      );

  static TextStyle get bodySmall => GoogleFonts.inter(
        fontSize: 14,
        height: 1.5,
        fontWeight: FontWeight.w400,
      );

  static TextStyle get bodyButton => GoogleFonts.inter(
        fontSize: 15,
        height: 1.2,
        fontWeight: FontWeight.w500,
      );

  static TextStyle get labelMicro => GoogleFonts.inter(
        fontSize: 12,
        height: 1.3,
        fontWeight: FontWeight.w500,
        letterSpacing: 0.6, // +0.05em × 12px
      );

  // ── Mono (JetBrains Mono) — hash strings only ──────────────────────────
  static TextStyle get bodyMono => GoogleFonts.jetBrainsMono(
        fontSize: 14,
        height: 1.5,
        fontWeight: FontWeight.w400,
      );
}

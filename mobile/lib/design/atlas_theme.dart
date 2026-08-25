import 'package:flutter/material.dart';

import 'tokens/colours.dart';
import 'tokens/typography.dart';

/// The app's Material theme, in one place so tests and goldens render exactly
/// what ships rather than an approximation of it.
///
/// Material's own buttons are given `type.body.button` explicitly. Without
/// this they inherit the default typography, which resolves to the platform
/// font — SF Pro on iOS, Roboto on Android — so the same screen shipped two
/// different button faces. `tokens.md §type.body.button` specifies Inter
/// 15/1.2/500 for button labels, and `AtlasButton` already honoured it; these
/// five call sites did not:
///
///   winner_claim_screen.dart  FilledButton   "Claim prize"
///   otp_screen.dart           TextButton     "Resend"
///   skill_question_screen.dart OutlinedButton "Next question" x2
///   skill_question_screen.dart FilledButton   "Submit answer"
ThemeData atlasTheme() {
  return ThemeData(
    useMaterial3: true,
    scaffoldBackgroundColor: AtlasColors.surfaceBase,
    colorScheme: const ColorScheme.light(
      primary: AtlasColors.brandPrimary,
      onPrimary: AtlasColors.textInverted,
      secondary: AtlasColors.brandAccent,
      surface: AtlasColors.surfaceBase,
      onSurface: AtlasColors.textPrimary,
      error: AtlasColors.stateDanger,
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor: AtlasColors.surfaceBase,
      foregroundColor: AtlasColors.textPrimary,
      elevation: 0,
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(textStyle: AtlasType.bodyButton),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(textStyle: AtlasType.bodyButton),
    ),
    textButtonTheme: TextButtonThemeData(
      style: TextButton.styleFrom(textStyle: AtlasType.bodyButton),
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(textStyle: AtlasType.bodyButton),
    ),
  );
}

import 'package:flutter/material.dart';

/// Elevation tokens per `_bmad-output/planning-artifacts/design/tokens.md §5`.
/// Three levels only. Warm-tinted shadows (never pure black).
class AtlasElevation {
  const AtlasElevation._();

  /// Warm shadow base — a very dark warm brown, not black. `rgba(60, 45, 30, α)`.
  static const Color _shadowTint = Color.fromRGBO(60, 45, 30, 1);

  /// Flat. Default for sections, table rows, inline content.
  static const List<BoxShadow> e0 = <BoxShadow>[];

  /// Raised card — draw cards, ticket cards, admin cards, dropdown menus.
  static List<BoxShadow> get e1 => [
        BoxShadow(
          color: _shadowTint.withOpacity(0.06),
          offset: const Offset(0, 1),
          blurRadius: 2,
        ),
        BoxShadow(
          color: _shadowTint.withOpacity(0.04),
          offset: const Offset(0, 2),
          blurRadius: 8,
        ),
      ];

  /// Overlay — modal, dialog, toast. At most one active per screen.
  static List<BoxShadow> get e2 => [
        BoxShadow(
          color: _shadowTint.withOpacity(0.08),
          offset: const Offset(0, 4),
          blurRadius: 12,
        ),
        BoxShadow(
          color: _shadowTint.withOpacity(0.06),
          offset: const Offset(0, 12),
          blurRadius: 32,
        ),
      ];
}

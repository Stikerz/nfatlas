import 'package:flutter/material.dart';

import '../tokens/colours.dart';
import '../tokens/radii.dart';
import '../tokens/spacing.dart';
import '../tokens/typography.dart';

/// AtlasToast — ephemeral notification of a completed micro-action.
/// Spec: `_bmad-output/planning-artifacts/design/components.md §16`.
enum AtlasToastVariant { defaultVariant, success, attention, danger }

class AtlasToast {
  const AtlasToast._();

  /// Shows a toast at the bottom of the screen (mobile default per §16.3).
  static void show(
    BuildContext context, {
    required String message,
    AtlasToastVariant variant = AtlasToastVariant.defaultVariant,
    Duration? duration,
  }) {
    final resolvedDuration = duration ??
        (variant == AtlasToastVariant.danger
            ? const Duration(seconds: 5)
            : const Duration(seconds: 3));

    final messenger = ScaffoldMessenger.of(context);
    messenger
      ..clearSnackBars()
      ..showSnackBar(
        SnackBar(
          duration: resolvedDuration,
          backgroundColor: variant == AtlasToastVariant.danger
              ? AtlasColors.stateDanger
              : AtlasColors.surfaceInverted,
          behavior: SnackBarBehavior.floating,
          margin: const EdgeInsets.all(AtlasSpace.s400),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AtlasRadius.medium),
          ),
          content: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (variant == AtlasToastVariant.success) ...[
                const Icon(Icons.check_circle,
                    size: 16, color: AtlasColors.stateSuccess),
                const SizedBox(width: AtlasSpace.s200),
              ] else if (variant == AtlasToastVariant.attention) ...[
                const Icon(Icons.warning_amber_rounded,
                    size: 16, color: AtlasColors.stateAttention),
                const SizedBox(width: AtlasSpace.s200),
              ],
              Flexible(
                child: Text(
                  message,
                  style: AtlasType.bodySmall.copyWith(
                    color: AtlasColors.textInverted,
                  ),
                ),
              ),
            ],
          ),
          action: variant == AtlasToastVariant.danger
              ? SnackBarAction(
                  label: 'Dismiss',
                  textColor: AtlasColors.textInverted,
                  onPressed: messenger.hideCurrentSnackBar,
                )
              : null,
        ),
      );
  }
}

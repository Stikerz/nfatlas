import 'package:flutter/material.dart';

import '../tokens/colours.dart';
import '../tokens/radii.dart';
import '../tokens/spacing.dart';
import '../tokens/typography.dart';

/// AtlasBanner — top-of-content region notification.
/// Spec: `_bmad-output/planning-artifacts/design/components.md §9`.
enum AtlasBannerVariant { info, success, attention, danger }

class AtlasBannerAction {
  const AtlasBannerAction({required this.label, required this.onPressed});
  final String label;
  final VoidCallback onPressed;
}

class AtlasBanner extends StatelessWidget {
  const AtlasBanner({
    super.key,
    required this.body,
    this.variant = AtlasBannerVariant.info,
    this.headline,
    this.dismissible = true,
    this.onDismiss,
    this.actions = const [],
  });

  final String body;
  final AtlasBannerVariant variant;
  final String? headline;
  final bool dismissible;
  final VoidCallback? onDismiss;
  final List<AtlasBannerAction> actions;

  Color get _accent {
    switch (variant) {
      case AtlasBannerVariant.info:
        return AtlasColors.brandPrimary;
      case AtlasBannerVariant.success:
        return AtlasColors.stateSuccess;
      case AtlasBannerVariant.attention:
        return AtlasColors.stateAttention;
      case AtlasBannerVariant.danger:
        return AtlasColors.stateDanger;
    }
  }

  bool get _isAlert =>
      variant == AtlasBannerVariant.danger ||
      variant == AtlasBannerVariant.attention;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      liveRegion: true,
      container: true,
      label: _isAlert ? 'alert' : 'status',
      child: DecoratedBox(
        decoration: BoxDecoration(
          color: _accent.withOpacity(0.12),
          borderRadius: BorderRadius.circular(AtlasRadius.medium),
          border: Border(left: BorderSide(color: _accent, width: 4)),
        ),
        child: Padding(
          padding: const EdgeInsets.all(AtlasSpace.s400),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (headline != null)
                      Text(
                        headline!,
                        style: AtlasType.bodyEmphasis.copyWith(color: _accent),
                      ),
                    if (headline != null) const SizedBox(height: AtlasSpace.s100),
                    Text(
                      body,
                      style: AtlasType.bodyDefault.copyWith(color: _accent),
                    ),
                    if (actions.isNotEmpty) ...[
                      const SizedBox(height: AtlasSpace.s300),
                      Wrap(
                        spacing: AtlasSpace.s300,
                        children: [
                          for (final action in actions)
                            TextButton(
                              onPressed: action.onPressed,
                              style: TextButton.styleFrom(
                                foregroundColor: _accent,
                                padding: EdgeInsets.zero,
                                textStyle: AtlasType.bodyButton,
                              ),
                              child: Text(action.label),
                            ),
                        ],
                      ),
                    ],
                  ],
                ),
              ),
              if (dismissible && onDismiss != null)
                IconButton(
                  icon: const Icon(Icons.close, size: 18),
                  color: _accent,
                  tooltip: 'Dismiss',
                  onPressed: onDismiss,
                ),
            ],
          ),
        ),
      ),
    );
  }
}

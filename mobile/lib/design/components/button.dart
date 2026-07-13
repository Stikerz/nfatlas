import 'package:flutter/material.dart';

import '../tokens/colours.dart';
import '../tokens/radii.dart';
import '../tokens/spacing.dart';
import '../tokens/typography.dart';

/// AtlasButton — the default interactive commitment element.
/// Spec: `_bmad-output/planning-artifacts/design/components.md §3`.
enum AtlasButtonVariant { primary, secondary, danger }

enum AtlasButtonSize { medium, large }

enum AtlasButtonWidth { auto, full }

class AtlasButton extends StatelessWidget {
  const AtlasButton({
    super.key,
    required this.label,
    required this.onPressed,
    this.variant = AtlasButtonVariant.primary,
    this.size = AtlasButtonSize.medium,
    this.width = AtlasButtonWidth.auto,
    this.loading = false,
    this.loadingLabel,
    this.leadingIcon,
    this.trailingIcon,
    this.attentionHint = false,
  });

  final String label;
  final VoidCallback? onPressed;
  final AtlasButtonVariant variant;
  final AtlasButtonSize size;
  final AtlasButtonWidth width;
  final bool loading;
  final String? loadingLabel;
  final IconData? leadingIcon;
  final IconData? trailingIcon;

  /// §3.4 bounded exception: primary variant only, irreversible-action pattern
  /// per wf-09 §5.4 / wf-11 §2.1 / wf-12 §2.1.
  final bool attentionHint;

  bool get _disabled => onPressed == null;

  double get _height => size == AtlasButtonSize.large ? 52 : 48;
  double get _horizontalPadding =>
      size == AtlasButtonSize.large ? AtlasSpace.s600 : AtlasSpace.s400;

  @override
  Widget build(BuildContext context) {
    final content = _buildContent();
    final child = SizedBox(
      height: _height,
      width: width == AtlasButtonWidth.full ? double.infinity : null,
      child: _wrapForVariant(context, content),
    );
    return Semantics(button: true, enabled: !_disabled, child: child);
  }

  Widget _buildContent() {
    if (loading) {
      return Row(
        mainAxisAlignment: MainAxisAlignment.center,
        mainAxisSize: MainAxisSize.min,
        children: [
          const SizedBox(
            width: 16,
            height: 16,
            child: CircularProgressIndicator(strokeWidth: 2),
          ),
          if (loadingLabel != null) ...[
            const SizedBox(width: AtlasSpace.s200),
            Text(loadingLabel!, style: AtlasType.bodyButton),
          ],
        ],
      );
    }
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      mainAxisSize: MainAxisSize.min,
      children: [
        if (leadingIcon != null) ...[
          Icon(leadingIcon, size: 18, semanticLabel: null),
          const SizedBox(width: AtlasSpace.s200),
        ],
        Text(label, style: AtlasType.bodyButton),
        if (trailingIcon != null) ...[
          const SizedBox(width: AtlasSpace.s200),
          Icon(trailingIcon, size: 18, semanticLabel: null),
        ],
      ],
    );
  }

  Widget _wrapForVariant(BuildContext context, Widget content) {
    switch (variant) {
      case AtlasButtonVariant.primary:
        return _PrimaryButton(
          onPressed: loading ? null : onPressed,
          horizontalPadding: _horizontalPadding,
          attentionHint: attentionHint,
          disabled: _disabled,
          child: content,
        );
      case AtlasButtonVariant.secondary:
        return _SecondaryButton(
          onPressed: loading ? null : onPressed,
          horizontalPadding: _horizontalPadding,
          disabled: _disabled,
          child: content,
        );
      case AtlasButtonVariant.danger:
        return _DangerButton(
          onPressed: loading ? null : onPressed,
          horizontalPadding: _horizontalPadding,
          disabled: _disabled,
          child: content,
        );
    }
  }
}

class _PrimaryButton extends StatelessWidget {
  const _PrimaryButton({
    required this.onPressed,
    required this.horizontalPadding,
    required this.attentionHint,
    required this.disabled,
    required this.child,
  });

  final VoidCallback? onPressed;
  final double horizontalPadding;
  final bool attentionHint;
  final bool disabled;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    final Color fillColor = disabled
        ? AtlasColors.surfaceElevated
        : AtlasColors.brandPrimary;
    final Color textColor =
        disabled ? AtlasColors.textSecondary : AtlasColors.textInverted;

    final button = ElevatedButton(
      onPressed: onPressed,
      style: ElevatedButton.styleFrom(
        backgroundColor: fillColor,
        foregroundColor: textColor,
        disabledBackgroundColor: AtlasColors.surfaceElevated,
        disabledForegroundColor: AtlasColors.textSecondary,
        padding: EdgeInsets.symmetric(horizontal: horizontalPadding),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AtlasRadius.medium),
        ),
        elevation: 0,
        textStyle: AtlasType.bodyButton,
      ),
      child: DefaultTextStyle.merge(
        style: TextStyle(color: textColor),
        child: child,
      ),
    );

    if (attentionHint && !disabled) {
      return Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(AtlasRadius.medium),
          color: AtlasColors.stateAttention.withOpacity(0.12),
        ),
        child: button,
      );
    }
    return button;
  }
}

class _SecondaryButton extends StatelessWidget {
  const _SecondaryButton({
    required this.onPressed,
    required this.horizontalPadding,
    required this.disabled,
    required this.child,
  });

  final VoidCallback? onPressed;
  final double horizontalPadding;
  final bool disabled;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    final Color colour =
        disabled ? AtlasColors.textSecondary : AtlasColors.brandPrimary;
    return OutlinedButton(
      onPressed: onPressed,
      style: OutlinedButton.styleFrom(
        foregroundColor: colour,
        side: BorderSide(color: colour, width: 1),
        padding: EdgeInsets.symmetric(horizontal: horizontalPadding),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AtlasRadius.medium),
        ),
        textStyle: AtlasType.bodyButton,
      ),
      child: DefaultTextStyle.merge(
        style: TextStyle(color: colour),
        child: child,
      ),
    );
  }
}

class _DangerButton extends StatelessWidget {
  const _DangerButton({
    required this.onPressed,
    required this.horizontalPadding,
    required this.disabled,
    required this.child,
  });

  final VoidCallback? onPressed;
  final double horizontalPadding;
  final bool disabled;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    final Color colour =
        disabled ? AtlasColors.textSecondary : AtlasColors.stateDanger;
    return TextButton(
      onPressed: onPressed,
      style: TextButton.styleFrom(
        foregroundColor: colour,
        padding: EdgeInsets.symmetric(horizontal: horizontalPadding),
        textStyle: AtlasType.bodyButton,
      ),
      child: DefaultTextStyle.merge(
        style: TextStyle(color: colour),
        child: child,
      ),
    );
  }
}

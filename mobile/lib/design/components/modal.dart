import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../tokens/colours.dart';
import '../tokens/elevation.dart';
import '../tokens/radii.dart';
import '../tokens/spacing.dart';
import '../tokens/typography.dart';
import 'button.dart';

/// AtlasModal — centred dialog for confirmations and focused interactions.
/// Every irreversible action (Cancel, Publish, Close, Reveal, Export) goes
/// through this per components.md §15.
class AtlasModalCta {
  const AtlasModalCta({
    required this.label,
    required this.onPressed,
    this.loading = false,
  });
  final String label;
  final VoidCallback onPressed;
  final bool loading;
}

Future<T?> showAtlasModal<T>({
  required BuildContext context,
  required String headline,
  required Widget body,
  required AtlasModalCta primaryCta,
  required AtlasModalCta secondaryCta,
  String? eyebrow,
  bool dismissOnBackdrop = true,
  bool dismissOnEscape = true,
  String? typeToConfirm,
  AtlasButtonVariant primaryVariant = AtlasButtonVariant.primary,
}) {
  return showDialog<T>(
    context: context,
    barrierDismissible: dismissOnBackdrop,
    barrierColor: AtlasColors.surfaceInverted.withOpacity(0.60),
    builder: (_) => _AtlasModal(
      headline: headline,
      body: body,
      primaryCta: primaryCta,
      secondaryCta: secondaryCta,
      eyebrow: eyebrow,
      dismissOnEscape: dismissOnEscape,
      typeToConfirm: typeToConfirm,
      primaryVariant: primaryVariant,
    ),
  );
}

class _AtlasModal extends StatefulWidget {
  const _AtlasModal({
    required this.headline,
    required this.body,
    required this.primaryCta,
    required this.secondaryCta,
    required this.eyebrow,
    required this.dismissOnEscape,
    required this.typeToConfirm,
    required this.primaryVariant,
  });

  final String headline;
  final Widget body;
  final AtlasModalCta primaryCta;
  final AtlasModalCta secondaryCta;
  final String? eyebrow;
  final bool dismissOnEscape;
  final String? typeToConfirm;
  final AtlasButtonVariant primaryVariant;

  @override
  State<_AtlasModal> createState() => _AtlasModalState();
}

class _AtlasModalState extends State<_AtlasModal> {
  final TextEditingController _confirmController = TextEditingController();
  bool _confirmMatched = false;

  bool get _primaryEnabled {
    if (widget.typeToConfirm == null) return true;
    return _confirmMatched;
  }

  @override
  void dispose() {
    _confirmController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Center(
      child: CallbackShortcuts(
        bindings: {
          if (widget.dismissOnEscape)
            const SingleActivator(LogicalKeyboardKey.escape):
                widget.secondaryCta.onPressed,
        },
        child: FocusScope(
          autofocus: true,
          child: Semantics(
            container: true,
            explicitChildNodes: true,
            label: widget.headline,
            child: Material(
              color: Colors.transparent,
              child: Container(
                width: 520,
                margin: const EdgeInsets.symmetric(horizontal: AtlasSpace.s400),
                padding: const EdgeInsets.all(AtlasSpace.s800),
                decoration: BoxDecoration(
                  color: AtlasColors.surfaceBase,
                  borderRadius: BorderRadius.circular(AtlasRadius.large),
                  boxShadow: AtlasElevation.e2,
                ),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (widget.eyebrow != null) ...[
                      Text(
                        widget.eyebrow!.toUpperCase(),
                        style: AtlasType.labelMicro
                            .copyWith(color: AtlasColors.brandAccent),
                      ),
                      const SizedBox(height: AtlasSpace.s200),
                    ],
                    Text(widget.headline, style: AtlasType.displayCard),
                    const SizedBox(height: AtlasSpace.s400),
                    DefaultTextStyle.merge(
                      style: AtlasType.bodyDefault,
                      child: widget.body,
                    ),
                    if (widget.typeToConfirm != null) ...[
                      const SizedBox(height: AtlasSpace.s600),
                      Text(
                        'Type ${widget.typeToConfirm} to confirm',
                        style: AtlasType.bodySmall
                            .copyWith(color: AtlasColors.textSecondary),
                      ),
                      const SizedBox(height: AtlasSpace.s200),
                      TextField(
                        controller: _confirmController,
                        autofocus: true,
                        autocorrect: false,
                        onChanged: (v) => setState(
                          () => _confirmMatched = v == widget.typeToConfirm,
                        ),
                        decoration: const InputDecoration(
                          border: OutlineInputBorder(),
                        ),
                      ),
                      Semantics(
                        liveRegion: true,
                        child: Text(
                          _primaryEnabled
                              ? 'Confirmation matched.'
                              : 'Confirmation not yet matched.',
                          style: AtlasType.bodySmall.copyWith(
                            color: AtlasColors.textSecondary,
                          ),
                        ),
                      ),
                    ],
                    const SizedBox(height: AtlasSpace.s800),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        AtlasButton(
                          label: widget.secondaryCta.label,
                          variant: AtlasButtonVariant.secondary,
                          onPressed: widget.secondaryCta.onPressed,
                        ),
                        const SizedBox(width: AtlasSpace.s300),
                        AtlasButton(
                          label: widget.primaryCta.label,
                          variant: widget.primaryVariant,
                          loading: widget.primaryCta.loading,
                          onPressed: _primaryEnabled
                              ? widget.primaryCta.onPressed
                              : null,
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

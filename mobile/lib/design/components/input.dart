import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:intl/intl.dart';

import '../tokens/colours.dart';
import '../tokens/radii.dart';
import '../tokens/spacing.dart';
import '../tokens/typography.dart';

/// AtlasInput — every field the user types into.
/// Spec: `_bmad-output/planning-artifacts/design/components.md §4`.
enum AtlasInputVariant { text, password, number, phone, date, otp }

class AtlasInput extends StatefulWidget {
  const AtlasInput({
    super.key,
    required this.label,
    required this.onChanged,
    this.variant = AtlasInputVariant.text,
    this.value,
    this.placeholder,
    this.helper,
    this.required = false,
    this.disabled = false,
    this.error,
    this.autofillHint,
    this.onBlur,
    this.readOnlyVerified = false,
    this.otpLength = 6,
    this.dateMin,
    this.dateMax,
  });

  final String label;
  final ValueChanged<String> onChanged;
  final AtlasInputVariant variant;
  final String? value;
  final String? placeholder;
  final String? helper;
  final bool required;
  final bool disabled;
  final String? error;
  final String? autofillHint;
  final VoidCallback? onBlur;
  final bool readOnlyVerified;
  final int otpLength;
  final DateTime? dateMin;
  final DateTime? dateMax;

  @override
  State<AtlasInput> createState() => _AtlasInputState();
}

class _AtlasInputState extends State<AtlasInput> {
  late final TextEditingController _controller;
  late final FocusNode _focusNode;
  bool _obscure = true;

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController(text: widget.value ?? '');
    _focusNode = FocusNode();
    _focusNode.addListener(_handleFocusChange);
  }

  @override
  void dispose() {
    _focusNode.removeListener(_handleFocusChange);
    _focusNode.dispose();
    _controller.dispose();
    super.dispose();
  }

  void _handleFocusChange() {
    if (!_focusNode.hasFocus) {
      widget.onBlur?.call();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildLabel(),
        const SizedBox(height: AtlasSpace.s100),
        _buildField(context),
        if (widget.error != null) ...[
          const SizedBox(height: AtlasSpace.s100),
          Text(
            widget.error!,
            style: AtlasType.bodySmall.copyWith(color: AtlasColors.stateDanger),
          ),
        ] else if (widget.helper != null) ...[
          const SizedBox(height: AtlasSpace.s100),
          Text(
            widget.helper!,
            style:
                AtlasType.bodySmall.copyWith(color: AtlasColors.textSecondary),
          ),
        ],
      ],
    );
  }

  Widget _buildLabel() {
    return RichText(
      text: TextSpan(
        style: AtlasType.labelMicro.copyWith(
          color: AtlasColors.textSecondary,
        ),
        children: [
          if (widget.required)
            const TextSpan(
              text: '▪ ',
              style: TextStyle(color: AtlasColors.brandAccent),
            ),
          TextSpan(text: widget.label.toUpperCase()),
        ],
      ),
    );
  }

  Widget _buildField(BuildContext context) {
    switch (widget.variant) {
      case AtlasInputVariant.otp:
        return _OtpField(
          length: widget.otpLength,
          disabled: widget.disabled,
          error: widget.error != null,
          onChanged: widget.onChanged,
        );
      case AtlasInputVariant.date:
        return _DateField(
          controller: _controller,
          disabled: widget.disabled,
          error: widget.error != null,
          readOnlyVerified: widget.readOnlyVerified,
          min: widget.dateMin,
          max: widget.dateMax,
          onChanged: widget.onChanged,
        );
      case AtlasInputVariant.phone:
        return _PhoneField(
          controller: _controller,
          focusNode: _focusNode,
          disabled: widget.disabled,
          error: widget.error != null,
          onChanged: widget.onChanged,
          placeholder: widget.placeholder,
        );
      case AtlasInputVariant.password:
        return _TextField(
          controller: _controller,
          focusNode: _focusNode,
          disabled: widget.disabled,
          error: widget.error != null,
          obscure: _obscure,
          keyboardType: TextInputType.visiblePassword,
          placeholder: widget.placeholder,
          onChanged: widget.onChanged,
          suffix: IconButton(
            icon: Icon(_obscure ? Icons.visibility : Icons.visibility_off),
            tooltip: _obscure ? 'Show password' : 'Hide password',
            onPressed: () => setState(() => _obscure = !_obscure),
          ),
        );
      case AtlasInputVariant.number:
        return _TextField(
          controller: _controller,
          focusNode: _focusNode,
          disabled: widget.disabled,
          error: widget.error != null,
          keyboardType: TextInputType.number,
          inputFormatters: [FilteringTextInputFormatter.digitsOnly],
          placeholder: widget.placeholder,
          onChanged: widget.onChanged,
        );
      case AtlasInputVariant.text:
        return _TextField(
          controller: _controller,
          focusNode: _focusNode,
          disabled: widget.disabled,
          error: widget.error != null,
          keyboardType: TextInputType.text,
          placeholder: widget.placeholder,
          onChanged: widget.onChanged,
        );
    }
  }
}

class _TextField extends StatelessWidget {
  const _TextField({
    required this.controller,
    required this.focusNode,
    required this.disabled,
    required this.error,
    required this.keyboardType,
    required this.onChanged,
    this.placeholder,
    this.obscure = false,
    this.inputFormatters,
    this.suffix,
  });

  final TextEditingController controller;
  final FocusNode focusNode;
  final bool disabled;
  final bool error;
  final TextInputType keyboardType;
  final ValueChanged<String> onChanged;
  final String? placeholder;
  final bool obscure;
  final List<TextInputFormatter>? inputFormatters;
  final Widget? suffix;

  @override
  Widget build(BuildContext context) {
    return TextField(
      controller: controller,
      focusNode: focusNode,
      enabled: !disabled,
      obscureText: obscure,
      keyboardType: keyboardType,
      inputFormatters: inputFormatters,
      style:
          AtlasType.bodyDefault.copyWith(color: AtlasColors.textPrimary),
      onChanged: onChanged,
      decoration: _atlasDecoration(
        placeholder: placeholder,
        disabled: disabled,
        error: error,
        suffix: suffix,
      ),
    );
  }
}

class _PhoneField extends StatelessWidget {
  const _PhoneField({
    required this.controller,
    required this.focusNode,
    required this.disabled,
    required this.error,
    required this.onChanged,
    this.placeholder,
  });

  final TextEditingController controller;
  final FocusNode focusNode;
  final bool disabled;
  final bool error;
  final ValueChanged<String> onChanged;
  final String? placeholder;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          height: 48,
          padding: const EdgeInsets.symmetric(horizontal: AtlasSpace.s300),
          decoration: BoxDecoration(
            color: AtlasColors.surfaceElevated,
            borderRadius: const BorderRadius.only(
              topLeft: Radius.circular(AtlasRadius.small),
              bottomLeft: Radius.circular(AtlasRadius.small),
            ),
            border: Border.all(color: AtlasColors.dividerHairline),
          ),
          alignment: Alignment.center,
          child: Text(
            '+234',
            style: AtlasType.bodyDefault
                .copyWith(color: AtlasColors.textPrimary),
          ),
        ),
        Expanded(
          child: TextField(
            controller: controller,
            focusNode: focusNode,
            enabled: !disabled,
            keyboardType: TextInputType.phone,
            inputFormatters: [
              FilteringTextInputFormatter.digitsOnly,
              LengthLimitingTextInputFormatter(10),
            ],
            onChanged: (v) => onChanged('+234$v'),
            style: AtlasType.bodyDefault
                .copyWith(color: AtlasColors.textPrimary),
            decoration: _atlasDecoration(
              placeholder: placeholder ?? '8030000000',
              disabled: disabled,
              error: error,
              radiusOverride: const BorderRadius.only(
                topRight: Radius.circular(AtlasRadius.small),
                bottomRight: Radius.circular(AtlasRadius.small),
              ),
            ),
          ),
        ),
      ],
    );
  }
}

class _DateField extends StatelessWidget {
  const _DateField({
    required this.controller,
    required this.disabled,
    required this.error,
    required this.readOnlyVerified,
    required this.onChanged,
    this.min,
    this.max,
  });

  final TextEditingController controller;
  final bool disabled;
  final bool error;
  final bool readOnlyVerified;
  final ValueChanged<String> onChanged;
  final DateTime? min;
  final DateTime? max;

  Future<void> _pick(BuildContext context) async {
    if (readOnlyVerified) return;
    final now = DateTime.now();
    final picked = await showDatePicker(
      context: context,
      initialDate: max ?? now,
      firstDate: min ?? DateTime(1900),
      lastDate: max ?? now,
    );
    if (picked != null) {
      final formatted = DateFormat('yyyy-MM-dd').format(picked);
      controller.text = formatted;
      onChanged(formatted);
    }
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: disabled ? null : () => _pick(context),
      child: AbsorbPointer(
        child: TextField(
          controller: controller,
          enabled: !disabled,
          style: AtlasType.bodyDefault
              .copyWith(color: AtlasColors.textPrimary),
          decoration: _atlasDecoration(
            placeholder: 'YYYY-MM-DD',
            disabled: disabled,
            error: error,
            suffix: readOnlyVerified
                ? const Padding(
                    padding: EdgeInsets.only(right: AtlasSpace.s300),
                    child: _VerifiedChip(),
                  )
                : const Icon(Icons.calendar_today, size: 18),
          ),
        ),
      ),
    );
  }
}

class _VerifiedChip extends StatelessWidget {
  const _VerifiedChip();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AtlasSpace.s200,
        vertical: AtlasSpace.s100,
      ),
      decoration: BoxDecoration(
        color: AtlasColors.stateSuccess.withOpacity(0.12),
        borderRadius: BorderRadius.circular(AtlasRadius.small),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(Icons.check, size: 12, color: AtlasColors.stateSuccess),
          const SizedBox(width: AtlasSpace.s100),
          Text(
            'verified',
            style:
                AtlasType.labelMicro.copyWith(color: AtlasColors.stateSuccess),
          ),
        ],
      ),
    );
  }
}

class _OtpField extends StatelessWidget {
  const _OtpField({
    required this.length,
    required this.disabled,
    required this.error,
    required this.onChanged,
  });

  final int length;
  final bool disabled;
  final bool error;
  final ValueChanged<String> onChanged;

  @override
  Widget build(BuildContext context) {
    return TextField(
      enabled: !disabled,
      autofillHints: const [AutofillHints.oneTimeCode],
      keyboardType: TextInputType.number,
      inputFormatters: [
        FilteringTextInputFormatter.digitsOnly,
        LengthLimitingTextInputFormatter(length),
      ],
      textAlign: TextAlign.center,
      style: AtlasType.displayCard
          .copyWith(color: AtlasColors.textPrimary, letterSpacing: 8),
      decoration: _atlasDecoration(
        placeholder: '·' * length,
        disabled: disabled,
        error: error,
      ),
      onChanged: onChanged,
    );
  }
}

InputDecoration _atlasDecoration({
  required String? placeholder,
  required bool disabled,
  required bool error,
  Widget? suffix,
  BorderRadius? radiusOverride,
}) {
  final radius =
      radiusOverride ?? BorderRadius.circular(AtlasRadius.small);
  final borderColour =
      error ? AtlasColors.stateDanger : AtlasColors.dividerHairline;
  return InputDecoration(
    hintText: placeholder,
    hintStyle:
        AtlasType.bodyDefault.copyWith(color: AtlasColors.textSecondary),
    contentPadding: const EdgeInsets.symmetric(
      horizontal: AtlasSpace.s300,
      vertical: AtlasSpace.s300,
    ),
    filled: true,
    fillColor: disabled
        ? AtlasColors.surfaceElevated
        : AtlasColors.surfaceBase,
    suffixIcon: suffix,
    enabledBorder: OutlineInputBorder(
      borderRadius: radius,
      borderSide: BorderSide(color: borderColour),
    ),
    focusedBorder: OutlineInputBorder(
      borderRadius: radius,
      borderSide: BorderSide(color: AtlasColors.focusRing, width: 2),
    ),
    errorBorder: OutlineInputBorder(
      borderRadius: radius,
      borderSide: const BorderSide(color: AtlasColors.stateDanger),
    ),
    disabledBorder: OutlineInputBorder(
      borderRadius: radius,
      borderSide: BorderSide(color: AtlasColors.dividerHairline),
    ),
  );
}

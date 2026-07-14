import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../design/components/banner.dart';
import '../../design/components/button.dart';
import '../../design/components/input.dart';
import '../../design/tokens/colours.dart';
import '../../design/tokens/spacing.dart';
import '../../design/tokens/typography.dart';
import 'identity_controller.dart';
import 'otp_screen.dart';

/// wf-01 Screen 1.1 — Register (email + phone + DOB + consent).
/// Spec: `_bmad-output/planning-artifacts/design/wireframes/01-register-otp-login.md §2`.
class RegisterScreen extends ConsumerStatefulWidget {
  const RegisterScreen({super.key});

  @override
  ConsumerState<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends ConsumerState<RegisterScreen> {
  String _emailError = '';
  String _phoneError = '';

  Future<void> _pickDob() async {
    final now = DateTime.now();
    final initial = ref.read(identityControllerProvider).dateOfBirth ??
        DateTime(now.year - 30, now.month, now.day);
    final picked = await showDatePicker(
      context: context,
      initialDate: initial,
      firstDate: DateTime(1900),
      lastDate: now,
    );
    if (picked != null && mounted) {
      ref.read(identityControllerProvider.notifier).setDateOfBirth(picked);
    }
  }

  Future<void> _submit() async {
    final controller = ref.read(identityControllerProvider.notifier);
    final ok = await controller.submitRegister();
    if (!mounted || !ok) return;
    await Navigator.of(context).push<void>(
      MaterialPageRoute<void>(builder: (_) => const OtpScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(identityControllerProvider);
    final controller = ref.read(identityControllerProvider.notifier);
    final dob = state.dateOfBirth;
    final now = DateTime.now();
    final under18 = dob != null && !IdentityController.isAtLeast18(dob, now);

    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: BackButton(color: AtlasColors.textPrimary),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: AtlasSpace.s600),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: AtlasSpace.s1200),
              Text(
                'Atlas',
                style: AtlasType.displayCard.copyWith(
                  color: AtlasColors.brandPrimary,
                ),
              ),
              const SizedBox(height: AtlasSpace.s800),
              Text('Create an account', style: AtlasType.displaySection),
              const SizedBox(height: AtlasSpace.s400),
              Text(
                "We'll send a one-time code to your phone. Takes about a minute.",
                style: AtlasType.bodyDefault.copyWith(
                  color: AtlasColors.textSecondary,
                ),
              ),
              const SizedBox(height: AtlasSpace.s800),
              if (state.error != null) ...[
                AtlasBanner(
                  variant: AtlasBannerVariant.danger,
                  body: state.error!,
                  onDismiss: () {},
                ),
                const SizedBox(height: AtlasSpace.s400),
              ],
              AtlasInput(
                label: 'Email',
                placeholder: 'you@domain.com',
                autofillHint: AutofillHints.email,
                error: _emailError.isEmpty ? null : _emailError,
                onChanged: controller.setEmail,
                onBlur: () {
                  final v = state.email;
                  setState(() {
                    _emailError = v.isEmpty || IdentityController.emailWellFormed(v)
                        ? ''
                        : 'Check the email — it needs an @ and a domain.';
                  });
                },
              ),
              const SizedBox(height: AtlasSpace.s400),
              AtlasInput(
                label: 'Phone (Nigerian mobile)',
                variant: AtlasInputVariant.phone,
                placeholder: '803 000 0000',
                error: _phoneError.isEmpty ? null : _phoneError,
                onChanged: controller.setPhoneE164,
                onBlur: () {
                  final v = state.phoneE164;
                  String err = '';
                  if (v.isNotEmpty && v.length < 14) {
                    err = 'Nigerian mobile numbers have 10 digits after +234.';
                  } else if (v.length == 14 && !RegExp(r'^\+234[789]').hasMatch(v)) {
                    err = 'Check the number — Nigerian mobiles start with 7, 8, or 9.';
                  }
                  setState(() => _phoneError = err);
                },
              ),
              const SizedBox(height: AtlasSpace.s400),
              _DobField(
                dob: dob,
                onTap: _pickDob,
                under18: under18,
              ),
              const SizedBox(height: AtlasSpace.s600),
              _TermsCheckbox(
                value: state.termsAccepted,
                onChanged: (v) => controller.setTermsAccepted(v ?? false),
              ),
              const SizedBox(height: AtlasSpace.s800),
              AtlasButton(
                label: state.busy ? 'Sending code…' : 'Continue',
                size: AtlasButtonSize.large,
                width: AtlasButtonWidth.full,
                loading: state.busy,
                onPressed: controller.canSubmitRegister && !state.busy ? _submit : null,
              ),
              const SizedBox(height: AtlasSpace.s400),
              Center(
                child: Text.rich(
                  TextSpan(
                    style: AtlasType.bodySmall
                        .copyWith(color: AtlasColors.textSecondary),
                    children: const [
                      TextSpan(text: 'Already have an account? '),
                      TextSpan(
                        text: 'Sign in',
                        style: TextStyle(
                          color: AtlasColors.brandPrimary,
                          fontWeight: FontWeight.w500,
                          decoration: TextDecoration.underline,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: AtlasSpace.s800),
            ],
          ),
        ),
      ),
    );
  }
}

class _DobField extends StatelessWidget {
  const _DobField({required this.dob, required this.onTap, required this.under18});

  final DateTime? dob;
  final VoidCallback onTap;
  final bool under18;

  @override
  Widget build(BuildContext context) {
    final formatted = dob == null ? '' : DateFormat('dd / MM / yyyy').format(dob!);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'DATE OF BIRTH',
          style: AtlasType.labelMicro.copyWith(color: AtlasColors.textSecondary),
        ),
        const SizedBox(height: AtlasSpace.s100),
        InkWell(
          onTap: onTap,
          child: Container(
            height: 48,
            padding: const EdgeInsets.symmetric(horizontal: AtlasSpace.s300),
            decoration: BoxDecoration(
              color: AtlasColors.surfaceBase,
              border: Border.all(
                color: under18 ? AtlasColors.stateDanger : AtlasColors.dividerHairline,
              ),
              borderRadius: BorderRadius.circular(4),
            ),
            alignment: Alignment.centerLeft,
            child: Text(
              formatted.isEmpty ? 'DD / MM / YYYY' : formatted,
              style: AtlasType.bodyDefault.copyWith(
                color: formatted.isEmpty
                    ? AtlasColors.textSecondary
                    : AtlasColors.textPrimary,
              ),
            ),
          ),
        ),
        const SizedBox(height: AtlasSpace.s100),
        Text(
          under18
              ? 'You must be 18 or over to use Atlas. Contact us if there’s been a mistake.'
              : 'You must be 18 or over to use Atlas.',
          style: AtlasType.bodySmall.copyWith(
            color: under18 ? AtlasColors.stateDanger : AtlasColors.textSecondary,
          ),
        ),
      ],
    );
  }
}

class _TermsCheckbox extends StatelessWidget {
  const _TermsCheckbox({required this.value, required this.onChanged});

  final bool value;
  final ValueChanged<bool?> onChanged;

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Checkbox(
          value: value,
          onChanged: onChanged,
          activeColor: AtlasColors.brandPrimary,
        ),
        Expanded(
          child: GestureDetector(
            onTap: () => onChanged(!value),
            child: Padding(
              padding: const EdgeInsets.only(top: AtlasSpace.s300),
              child: Text.rich(
                TextSpan(
                  style: AtlasType.bodyDefault
                      .copyWith(color: AtlasColors.textPrimary),
                  children: const [
                    TextSpan(text: 'I agree to the '),
                    TextSpan(
                      text: 'Terms',
                      style: TextStyle(
                        color: AtlasColors.brandPrimary,
                        decoration: TextDecoration.underline,
                      ),
                    ),
                    TextSpan(text: ' and '),
                    TextSpan(
                      text: 'Privacy Notice',
                      style: TextStyle(
                        color: AtlasColors.brandPrimary,
                        decoration: TextDecoration.underline,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../design/components/banner.dart';
import '../../design/components/button.dart';
import '../../design/components/input.dart';
import '../../design/tokens/colours.dart';
import '../../design/tokens/spacing.dart';
import '../../design/tokens/typography.dart';
import 'identity_controller.dart';
import 'welcome_screen.dart';

/// wf-01 Screen 1.3 — Create password.
class PasswordScreen extends ConsumerStatefulWidget {
  const PasswordScreen({super.key});

  @override
  ConsumerState<PasswordScreen> createState() => _PasswordScreenState();
}

class _PasswordScreenState extends ConsumerState<PasswordScreen> {
  String _password = '';

  bool get _rule10Chars => _password.length >= 10;
  bool get _ruleMix =>
      RegExp(r'[A-Za-z]').hasMatch(_password) &&
      RegExp(r'\d').hasMatch(_password);
  bool get _canSubmit => _rule10Chars && _ruleMix;

  Future<void> _submit() async {
    final ok =
        await ref.read(identityControllerProvider.notifier).submitPassword(_password);
    if (!mounted || !ok) return;
    await Navigator.of(context).pushReplacement<void, void>(
      MaterialPageRoute<void>(builder: (_) => const WelcomeScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(identityControllerProvider);

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
              Text('One more step', style: AtlasType.displaySection),
              const SizedBox(height: AtlasSpace.s400),
              Text(
                "Set a password. You'll use this to sign back in on any device.",
                style: AtlasType.bodyDefault
                    .copyWith(color: AtlasColors.textSecondary),
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
                label: 'Password',
                variant: AtlasInputVariant.password,
                onChanged: (v) => setState(() => _password = v),
              ),
              const SizedBox(height: AtlasSpace.s400),
              _rule(_rule10Chars, '10 characters or more'),
              _rule(_ruleMix, 'Mix of letters and numbers'),
              _rule(true, 'Not one you use for banking',
                  advisoryOnly: true),
              const SizedBox(height: AtlasSpace.s800),
              AtlasButton(
                label: state.busy ? 'Creating account…' : 'Create account',
                size: AtlasButtonSize.large,
                width: AtlasButtonWidth.full,
                loading: state.busy,
                onPressed:
                    _canSubmit && !state.busy ? _submit : null,
              ),
              const SizedBox(height: AtlasSpace.s400),
              Center(
                child: Text(
                  'By creating your account you accept the Terms and Privacy Notice.',
                  textAlign: TextAlign.center,
                  style: AtlasType.bodySmall
                      .copyWith(color: AtlasColors.textSecondary),
                ),
              ),
              const SizedBox(height: AtlasSpace.s800),
            ],
          ),
        ),
      ),
    );
  }

  Widget _rule(bool satisfied, String label, {bool advisoryOnly = false}) {
    final iconColour = satisfied
        ? AtlasColors.stateSuccess
        : (advisoryOnly ? AtlasColors.textSecondary : AtlasColors.textSecondary);
    final icon = satisfied ? Icons.check_circle : Icons.circle_outlined;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: AtlasSpace.s100),
      child: Row(
        children: [
          Icon(icon, size: 16, color: iconColour),
          const SizedBox(width: AtlasSpace.s200),
          Text(
            label,
            style: AtlasType.bodySmall
                .copyWith(color: AtlasColors.textSecondary),
          ),
        ],
      ),
    );
  }
}

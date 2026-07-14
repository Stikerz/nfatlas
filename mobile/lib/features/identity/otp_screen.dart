import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../design/components/banner.dart';
import '../../design/components/toast.dart';
import '../../design/tokens/colours.dart';
import '../../design/tokens/radii.dart';
import '../../design/tokens/spacing.dart';
import '../../design/tokens/typography.dart';
import 'identity_controller.dart';
import 'password_screen.dart';

/// wf-01 Screen 1.2 — OTP entry (6 segmented digit boxes, auto-verify on 6th).
class OtpScreen extends ConsumerStatefulWidget {
  const OtpScreen({super.key});

  @override
  ConsumerState<OtpScreen> createState() => _OtpScreenState();
}

class _OtpScreenState extends ConsumerState<OtpScreen> {
  final _controllers =
      List.generate(6, (_) => TextEditingController(), growable: false);
  final _focusNodes = List.generate(6, (_) => FocusNode(), growable: false);

  Timer? _resendTimer;
  int _cooldownSeconds = 60;
  bool _errored = false;

  @override
  void initState() {
    super.initState();
    _startCooldown();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _focusNodes.first.requestFocus();
    });
  }

  void _startCooldown() {
    _resendTimer?.cancel();
    setState(() => _cooldownSeconds = 60);
    _resendTimer = Timer.periodic(const Duration(seconds: 1), (t) {
      if (!mounted) {
        t.cancel();
        return;
      }
      setState(() => _cooldownSeconds -= 1);
      if (_cooldownSeconds <= 0) t.cancel();
    });
  }

  @override
  void dispose() {
    _resendTimer?.cancel();
    for (final c in _controllers) {
      c.dispose();
    }
    for (final f in _focusNodes) {
      f.dispose();
    }
    super.dispose();
  }

  Future<void> _onDigitChanged(int index, String value) async {
    if (value.length > 1) {
      // Paste path — spread across boxes.
      final digits = value.replaceAll(RegExp(r'\D'), '');
      for (var i = 0; i < 6; i++) {
        _controllers[i].text = i < digits.length ? digits[i] : '';
      }
      if (digits.length >= 6) {
        FocusScope.of(context).unfocus();
        await _verify();
      } else {
        _focusNodes[digits.length].requestFocus();
      }
      return;
    }

    if (value.isNotEmpty && index < 5) {
      _focusNodes[index + 1].requestFocus();
    }

    if (_controllers.every((c) => c.text.length == 1)) {
      await _verify();
    }
  }

  Future<void> _verify() async {
    final code = _controllers.map((c) => c.text).join();
    final ok = await ref.read(identityControllerProvider.notifier).submitOtp(code);
    if (!mounted) return;

    if (ok) {
      await Navigator.of(context).push<void>(
        MaterialPageRoute<void>(builder: (_) => const PasswordScreen()),
      );
    } else {
      setState(() => _errored = true);
      for (final c in _controllers) {
        c.clear();
      }
      _focusNodes.first.requestFocus();
      Future<void>.delayed(const Duration(milliseconds: 400), () {
        if (mounted) setState(() => _errored = false);
      });
    }
  }

  Future<void> _resend() async {
    final ok = await ref.read(identityControllerProvider.notifier).resendOtp();
    if (!mounted) return;
    if (ok) {
      AtlasToast.show(context, message: 'New code sent.');
      _startCooldown();
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(identityControllerProvider);
    final phone = state.phoneE164;

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
              Text('Enter the code', style: AtlasType.displaySection),
              const SizedBox(height: AtlasSpace.s400),
              Text(
                'Sent to $phone',
                style: AtlasType.bodyDefault
                    .copyWith(color: AtlasColors.textSecondary),
              ),
              const SizedBox(height: AtlasSpace.s100),
              Text(
                'Not you? Change number',
                style: AtlasType.bodyDefault.copyWith(
                  color: AtlasColors.brandPrimary,
                  decoration: TextDecoration.underline,
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
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: List.generate(6, (i) => _digitBox(i)),
              ),
              const SizedBox(height: AtlasSpace.s600),
              Text(
                _cooldownSeconds > 0
                    ? "Didn't get it? Resend in ${_cooldownSeconds}s"
                    : "Didn't get it? Resend",
                style: AtlasType.bodySmall.copyWith(
                  color: _cooldownSeconds > 0
                      ? AtlasColors.textSecondary
                      : AtlasColors.brandPrimary,
                ),
              ),
              const SizedBox(height: AtlasSpace.s400),
              if (_cooldownSeconds <= 0)
                TextButton(onPressed: _resend, child: const Text('Resend')),
            ],
          ),
        ),
      ),
    );
  }

  Widget _digitBox(int i) {
    return SizedBox(
      width: 48,
      height: 48,
      child: TextField(
        controller: _controllers[i],
        focusNode: _focusNodes[i],
        maxLength: i == 0 ? 6 : 1, // first box accepts full paste
        keyboardType: TextInputType.number,
        textAlign: TextAlign.center,
        autofillHints: const [AutofillHints.oneTimeCode],
        style: AtlasType.displayCard,
        inputFormatters: [FilteringTextInputFormatter.digitsOnly],
        decoration: InputDecoration(
          counterText: '',
          contentPadding: EdgeInsets.zero,
          filled: true,
          fillColor: AtlasColors.surfaceBase,
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(AtlasRadius.small),
            borderSide: BorderSide(
              color: _errored
                  ? AtlasColors.stateDanger
                  : AtlasColors.dividerHairline,
            ),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(AtlasRadius.small),
            borderSide: BorderSide(
              color: _errored ? AtlasColors.stateDanger : AtlasColors.focusRing,
              width: 2,
            ),
          ),
        ),
        onChanged: (v) => _onDigitChanged(i, v),
      ),
    );
  }
}

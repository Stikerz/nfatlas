import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../design/tokens/colours.dart';
import '../../design/tokens/spacing.dart';
import '../../design/tokens/typography.dart';
import '../identity/identity_api.dart';

/// Permanent account closure — ADR-010 Phase A, build-plan item A5.
///
/// Three deliberate properties, all of them compliance requirements rather
/// than UX preferences:
///
/// 1. **The limits are stated before the control, not after.** Phase A is
///    account-level. It does not stop the same person registering again
///    with a different email and phone — that needs BVN matching, which
///    depends on ADR-007 (KYC). Saying so up front is the whole point:
///    REVIEW-002 §6 found this page's web counterpart claiming a
///    protection that did not exist.
/// 2. **No persuasion.** No "are you sure you want to miss out", no
///    retention offer, no softer alternative presented as the easy path.
///    A user asking to stop is not a conversion problem.
/// 3. **Confirmation is typed, plus an OTP.** Matches ADR-010's
///    requirements; both are re-checked server-side, so a client bug
///    cannot close an account by accident.
class SelfExclusionScreen extends ConsumerStatefulWidget {
  const SelfExclusionScreen({super.key, required this.userId});

  final String userId;

  @override
  ConsumerState<SelfExclusionScreen> createState() =>
      _SelfExclusionScreenState();
}

class _SelfExclusionScreenState extends ConsumerState<SelfExclusionScreen> {
  final _confirmController = TextEditingController();
  final _otpController = TextEditingController();

  bool _otpRequested = false;
  bool _busy = false;
  String? _error;
  SelfExclusionResult? _done;

  @override
  void dispose() {
    _confirmController.dispose();
    _otpController.dispose();
    super.dispose();
  }

  bool get _confirmed => _confirmController.text.trim() == 'EXCLUDE';

  Future<void> _requestCode() async {
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      await ref
          .read(identityApiProvider)
          .issueOtp(userId: widget.userId, purpose: 'login_mfa');
      setState(() => _otpRequested = true);
    } on DioException catch (e) {
      setState(() => _error = 'Could not send the code: ${e.message}');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _close() async {
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      final result = await ref
          .read(identityApiProvider)
          .selfExclude(otpCode: _otpController.text.trim());
      setState(() => _done = result);
    } on DioException catch (e) {
      setState(() => _error = 'That did not work: ${e.message}');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Close my account')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(AtlasSpace.s400),
        child: _done != null ? _buildDone() : _buildForm(),
      ),
    );
  }

  Widget _buildDone() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Your account is closed', style: AtlasType.displayCard),
        const SizedBox(height: AtlasSpace.s300),
        Text(
          'You have been signed out everywhere. This account can no longer '
          'enter any draw, and we cannot reopen it.',
          style: AtlasType.bodyDefault,
        ),
        const SizedBox(height: AtlasSpace.s300),
        Text(
          'If you want help with gambling-related harm, the support '
          'resources on our Responsible play page are independent of Atlas '
          'and remain available to you.',
          style: AtlasType.bodySmall.copyWith(
            color: AtlasColors.textSecondary,
          ),
        ),
      ],
    );
  }

  Widget _buildForm() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('This cannot be undone', style: AtlasType.displayCard),
        const SizedBox(height: AtlasSpace.s300),
        Text(
          'Closing your account ends it permanently. You will be signed out '
          'on every device, you will not be able to enter any draw, and '
          'there is no way for us to reopen it — not by support request, '
          'not later, not at all.',
          style: AtlasType.bodyDefault,
        ),
        const SizedBox(height: AtlasSpace.s400),

        // The limit, stated before the control rather than buried after it.
        Container(
          padding: const EdgeInsets.all(AtlasSpace.s300),
          decoration: BoxDecoration(
            color: AtlasColors.surfaceElevated,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('What this does not do', style: AtlasType.bodyEmphasis),
              const SizedBox(height: AtlasSpace.s200),
              Text(
                'It closes this account. It does not currently stop someone '
                'opening a new one with a different email address and phone '
                'number. Making that impossible needs identity checks we '
                'have not built yet.\n\n'
                'If stopping matters to you, the independent support '
                'resources on our Responsible play page will help more than '
                'this button will.',
                style: AtlasType.bodySmall.copyWith(
                  color: AtlasColors.textSecondary,
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: AtlasSpace.s300),
        // REVIEW-002 Addendum B.3: a user closing an account with money in
        // it must not have to guess what happens to it. Phase A holds the
        // balance (no refund rail yet) — so say so, here, before they act.
        Text(
          'If you have money in your account, closing it does not forfeit '
          'the balance. We hold it and support will arrange payment to you.',
          style: AtlasType.bodySmall.copyWith(
            color: AtlasColors.textSecondary,
          ),
        ),
        const SizedBox(height: AtlasSpace.s400),

        Text('Type EXCLUDE to confirm', style: AtlasType.bodyEmphasis),
        const SizedBox(height: AtlasSpace.s200),
        TextField(
          controller: _confirmController,
          autocorrect: false,
          enableSuggestions: false,
          textCapitalization: TextCapitalization.characters,
          decoration: const InputDecoration(hintText: 'EXCLUDE'),
          onChanged: (_) => setState(() {}),
        ),
        const SizedBox(height: AtlasSpace.s400),

        if (!_otpRequested)
          FilledButton(
            onPressed: _confirmed && !_busy ? _requestCode : null,
            child: const Text('Send me a confirmation code'),
          )
        else ...[
          Text('Enter the code we sent you', style: AtlasType.bodyEmphasis),
          const SizedBox(height: AtlasSpace.s200),
          TextField(
            controller: _otpController,
            keyboardType: TextInputType.number,
            decoration: const InputDecoration(hintText: '123456'),
            onChanged: (_) => setState(() {}),
          ),
          const SizedBox(height: AtlasSpace.s400),
          FilledButton(
            onPressed: _confirmed && _otpController.text.trim().length >= 4 && !_busy
                ? _close
                : null,
            child: Text(_busy ? 'Closing…' : 'Close my account permanently'),
          ),
        ],

        if (_error != null) ...[
          const SizedBox(height: AtlasSpace.s300),
          Text(
            _error!,
            style: AtlasType.bodySmall.copyWith(color: AtlasColors.stateDanger),
          ),
        ],
      ],
    );
  }
}

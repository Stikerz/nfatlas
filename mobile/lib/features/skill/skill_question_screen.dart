import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../design/tokens/colours.dart';
import '../../design/tokens/spacing.dart';
import '../../design/tokens/typography.dart';
import '../draws/draws_api.dart';
import '../tickets/tickets_api.dart';
import 'skill_api.dart';

/// Enter-a-draw flow: skill question → answer → purchase intent →
/// external browser for Paystack checkout.
///
/// Push this screen with the target draw. After the user completes
/// checkout (or aborts), they navigate back — the tickets tab picks
/// up the pending intent on next refresh.
class SkillQuestionScreen extends ConsumerStatefulWidget {
  const SkillQuestionScreen({super.key, required this.draw});

  final DrawSummary draw;

  @override
  ConsumerState<SkillQuestionScreen> createState() =>
      _SkillQuestionScreenState();
}

class _SkillQuestionScreenState extends ConsumerState<SkillQuestionScreen> {
  SkillQuestion? _question;
  String? _selectedOptionId;
  bool _loading = true;
  bool _submitting = false;
  String? _error;
  _AnswerOutcome? _outcome;

  @override
  void initState() {
    super.initState();
    _loadNext();
  }

  Future<void> _loadNext() async {
    setState(() {
      _loading = true;
      _error = null;
      _outcome = null;
      _selectedOptionId = null;
    });
    try {
      final q = await ref.read(skillApiProvider).next(widget.draw.id);
      if (mounted) {
        setState(() {
          _question = q;
          _loading = false;
        });
      }
    } on DioException catch (exc) {
      if (mounted) {
        setState(() {
          _error = _extractError(exc, fallback: 'Could not load a question.');
          _loading = false;
        });
      }
    }
  }

  Future<void> _submit() async {
    final attemptId = _question?.attemptId;
    final optionId = _selectedOptionId;
    if (attemptId == null || optionId == null) return;

    setState(() {
      _submitting = true;
      _error = null;
    });
    try {
      final answer = await ref.read(skillApiProvider).answer(
            attemptId: attemptId,
            optionId: optionId,
          );
      if (!mounted) return;
      if (!answer.isCorrect) {
        setState(() {
          _submitting = false;
          _outcome = _AnswerOutcome.wrong;
        });
        return;
      }
      // Correct → mint the payment intent + open Paystack.
      final purchase = await ref.read(ticketsApiProvider).purchase(
            drawId: widget.draw.id,
            entitlementId: attemptId,
          );
      if (!mounted) return;
      setState(() {
        _submitting = false;
        _outcome = _AnswerOutcome.correct;
      });
      final url = purchase.checkoutUrl;
      if (url != null && url.isNotEmpty) {
        await launchUrl(Uri.parse(url), mode: LaunchMode.externalApplication);
      }
      // Invalidate providers so tickets tab reflects the pending intent
      // on the user's return.
      ref.invalidate(myTicketsProvider);
    } on DioException catch (exc) {
      if (mounted) {
        setState(() {
          _submitting = false;
          _error = _extractError(exc, fallback: 'Could not submit answer.');
        });
      }
    }
  }

  String _extractError(DioException exc, {required String fallback}) {
    final data = exc.response?.data;
    if (data is Map<String, dynamic>) {
      final detail = data['detail'];
      if (detail is Map<String, dynamic>) {
        final message = detail['message'];
        if (message is String) return message;
      }
    }
    return fallback;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Enter draw', style: AtlasType.displayCard),
        backgroundColor: AtlasColors.surfaceBase,
        elevation: 0,
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(AtlasSpace.s600),
          child: _loading
              ? const Center(child: CircularProgressIndicator())
              : _error != null
                  ? _errorPanel()
                  : _bodyPanel(),
        ),
      ),
    );
  }

  Widget _bodyPanel() {
    final q = _question;
    if (q == null) return const SizedBox.shrink();

    if (_outcome == _AnswerOutcome.correct) {
      return _CorrectPanel(prizeCopy: widget.draw.prizeCopy);
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          widget.draw.prizeCopy,
          style: AtlasType.bodyDefault.copyWith(color: AtlasColors.textSecondary),
        ),
        const SizedBox(height: AtlasSpace.s600),
        Text(q.prompt, style: AtlasType.displaySection),
        const SizedBox(height: AtlasSpace.s600),
        ...q.options.map((option) => _optionTile(option)),
        if (_outcome == _AnswerOutcome.wrong) ...[
          const SizedBox(height: AtlasSpace.s400),
          Text(
            'Not quite. Try another question.',
            style: AtlasType.bodyEmphasis.copyWith(color: AtlasColors.stateDanger),
          ),
          const SizedBox(height: AtlasSpace.s300),
          OutlinedButton(
            onPressed: _loadNext,
            child: const Text('Next question'),
          ),
        ] else ...[
          const SizedBox(height: AtlasSpace.s600),
          FilledButton(
            onPressed:
                _selectedOptionId == null || _submitting ? null : _submit,
            child: Text(_submitting ? 'Submitting…' : 'Submit answer'),
          ),
        ],
      ],
    );
  }

  Widget _optionTile(SkillOption option) {
    final selected = option.id == _selectedOptionId;
    return Padding(
      padding: const EdgeInsets.only(bottom: AtlasSpace.s300),
      child: InkWell(
        onTap: _submitting || _outcome == _AnswerOutcome.wrong
            ? null
            : () => setState(() => _selectedOptionId = option.id),
        borderRadius: BorderRadius.circular(AtlasSpace.s200),
        child: Container(
          padding: const EdgeInsets.all(AtlasSpace.s400),
          decoration: BoxDecoration(
            color: selected
                ? AtlasColors.brandPrimary.withOpacity(0.08)
                : AtlasColors.surfaceElevated,
            border: Border.all(
              color: selected
                  ? AtlasColors.brandPrimary
                  : AtlasColors.dividerHairline,
              width: selected ? 2 : 1,
            ),
            borderRadius: BorderRadius.circular(AtlasSpace.s200),
          ),
          child: Row(
            children: [
              Icon(
                selected
                    ? Icons.radio_button_checked
                    : Icons.radio_button_unchecked,
                color: selected
                    ? AtlasColors.brandPrimary
                    : AtlasColors.textSecondary,
              ),
              const SizedBox(width: AtlasSpace.s400),
              Expanded(
                child: Text(option.text, style: AtlasType.bodyDefault),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _errorPanel() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            _error ?? 'Something went wrong.',
            textAlign: TextAlign.center,
            style: AtlasType.bodyDefault.copyWith(color: AtlasColors.stateDanger),
          ),
          const SizedBox(height: AtlasSpace.s400),
          OutlinedButton(
            onPressed: _loadNext,
            child: const Text('Try again'),
          ),
        ],
      ),
    );
  }
}

enum _AnswerOutcome { correct, wrong }

class _CorrectPanel extends StatelessWidget {
  const _CorrectPanel({required this.prizeCopy});

  final String prizeCopy;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.check_circle,
              color: AtlasColors.stateSuccess, size: 64),
          const SizedBox(height: AtlasSpace.s400),
          Text('Correct answer', style: AtlasType.displaySection),
          const SizedBox(height: AtlasSpace.s300),
          Text(
            'We opened Paystack in your browser to complete the ₦500 ticket for:\n\n$prizeCopy',
            textAlign: TextAlign.center,
            style: AtlasType.bodyDefault.copyWith(color: AtlasColors.textSecondary),
          ),
          const SizedBox(height: AtlasSpace.s600),
          Text(
            'Your ticket will show under TICKETS when payment lands.',
            textAlign: TextAlign.center,
            style: AtlasType.bodySmall.copyWith(color: AtlasColors.textSecondary),
          ),
        ],
      ),
    );
  }
}

import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../design/tokens/colours.dart';
import '../../design/tokens/spacing.dart';
import '../../design/tokens/typography.dart';
import '../draws/draws_api.dart';
import 'tickets_api.dart';

/// Enter-a-draw flow: confirm → payment intent → external browser for
/// Paystack checkout.
///
/// Replaces `SkillQuestionScreen`, which ran the same flow behind a skill
/// question. The question was removed on 2026-11-26 (AMEND-003): it
/// bought Atlas nothing under the governing State law and may have been
/// adverse under the Lagos advertising code. Lawfulness now rests on the
/// State gaming licence, not on a draw mechanic.
///
/// Deliberately a confirm step rather than a one-tap buy. The entry is
/// paid and non-refundable, so the user should see the price and act on
/// it, not discover it afterwards.
class EntryPurchaseScreen extends ConsumerStatefulWidget {
  const EntryPurchaseScreen({super.key, required this.draw});

  final DrawSummary draw;

  @override
  ConsumerState<EntryPurchaseScreen> createState() =>
      _EntryPurchaseScreenState();
}

class _EntryPurchaseScreenState extends ConsumerState<EntryPurchaseScreen> {
  bool _submitting = false;
  String? _error;
  bool _launched = false;

  Future<void> _buy() async {
    setState(() {
      _submitting = true;
      _error = null;
    });
    try {
      final purchase =
          await ref.read(ticketsApiProvider).purchase(drawId: widget.draw.id);
      if (!mounted) return;
      final url = purchase.checkoutUrl;
      if (url != null && url.isNotEmpty) {
        await launchUrl(Uri.parse(url), mode: LaunchMode.externalApplication);
      }
      // Tickets tab picks up the pending intent on the user's return.
      ref.invalidate(myTicketsProvider);
      if (!mounted) return;
      setState(() {
        _submitting = false;
        _launched = true;
      });
    } on DioException catch (exc) {
      if (!mounted) return;
      setState(() {
        _submitting = false;
        _error = _extractError(exc, fallback: 'Could not start checkout.');
      });
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

  String get _price {
    final naira = widget.draw.ticketPriceMinor / 100;
    return '₦${naira.toStringAsFixed(naira.truncateToDouble() == naira ? 0 : 2)}';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Enter this draw')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(AtlasSpace.s400),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(widget.draw.prizeCopy, style: AtlasType.displayCard),
            const SizedBox(height: AtlasSpace.s400),
            Text('One entry', style: AtlasType.bodyEmphasis),
            const SizedBox(height: AtlasSpace.s200),
            Text(
              '$_price per entry. Payment is taken by Paystack in your '
              'browser; your ticket appears here once the payment confirms.',
              style: AtlasType.bodyDefault,
            ),
            const SizedBox(height: AtlasSpace.s300),
            Text(
              'Entries are not refundable once the draw closes. You can '
              'enter as many times as you like — each entry is one chance.',
              style: AtlasType.bodySmall.copyWith(
                color: AtlasColors.textSecondary,
              ),
            ),
            const SizedBox(height: AtlasSpace.s500),
            if (_launched)
              Text(
                'Checkout opened in your browser. Come back here when you '
                'are done and pull to refresh your tickets.',
                style: AtlasType.bodyDefault,
              )
            else
              FilledButton(
                onPressed: _submitting ? null : _buy,
                child: Text(
                  _submitting ? 'Opening checkout…' : 'Pay $_price and enter',
                ),
              ),
            if (_error != null) ...[
              const SizedBox(height: AtlasSpace.s300),
              Text(
                _error!,
                style: AtlasType.bodySmall
                    .copyWith(color: AtlasColors.stateDanger),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

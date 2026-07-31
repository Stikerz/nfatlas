import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../design/tokens/colours.dart';
import '../../design/tokens/spacing.dart';
import '../../design/tokens/typography.dart';
import '../tickets/tickets_api.dart';
import 'winners_api.dart';

/// Winner claim flow — reads the user's tickets, cross-references with
/// draw_winners for each revealed draw, and prompts the primary /
/// reserve winners to claim.
///
/// V0.5 simple shape: for each ticket in a revealed draw, we hit
/// GET /draws/{id}/winners to check if this user is on it. If yes,
/// render the CTA + POST /claim.
class WinnerClaimScreen extends ConsumerStatefulWidget {
  const WinnerClaimScreen({super.key});

  @override
  ConsumerState<WinnerClaimScreen> createState() => _WinnerClaimScreenState();
}

class _WinnerClaimScreenState extends ConsumerState<WinnerClaimScreen> {
  Future<List<_WinnerOpportunity>>? _future;

  @override
  void initState() {
    super.initState();
    _future = _loadOpportunities();
  }

  Future<List<_WinnerOpportunity>> _loadOpportunities() async {
    final tickets = await ref.read(ticketsApiProvider).listMine();
    final drawIds = tickets.map((t) => t.drawId).toSet();
    final winnersApi = ref.read(winnersApiProvider);

    final opportunities = <_WinnerOpportunity>[];
    for (final drawId in drawIds) {
      try {
        final winners = await winnersApi.listForDraw(drawId);
        for (final ticket in tickets.where((t) => t.drawId == drawId)) {
          final match = winners.firstWhere(
            (w) => w.ticketId == ticket.id,
            orElse: () => const WinnerSummary(
              position: -1,
              isPrimary: false,
              ticketId: '',
              userId: '',
              contactStatus: '',
            ),
          );
          if (match.ticketId.isNotEmpty) {
            opportunities.add(
              _WinnerOpportunity(
                drawId: drawId,
                ticketId: ticket.id,
                ticketNumber: ticket.ticketNumber,
                isPrimary: match.isPrimary,
                position: match.position,
                contactStatus: match.contactStatus,
              ),
            );
          }
        }
      } catch (_) {
        // Draw might not be revealed yet — skip.
      }
    }
    return opportunities;
  }

  Future<void> _refresh() async {
    setState(() {
      _future = _loadOpportunities();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Your wins', style: AtlasType.displayCard),
        backgroundColor: AtlasColors.surfaceBase,
        elevation: 0,
      ),
      body: SafeArea(
        child: FutureBuilder<List<_WinnerOpportunity>>(
          future: _future,
          builder: (context, snapshot) {
            if (snapshot.connectionState != ConnectionState.done) {
              return const Center(child: CircularProgressIndicator());
            }
            final data = snapshot.data ?? const <_WinnerOpportunity>[];
            if (data.isEmpty) {
              return _EmptyState();
            }
            return RefreshIndicator(
              onRefresh: _refresh,
              child: ListView.separated(
                padding: const EdgeInsets.all(AtlasSpace.s600),
                itemCount: data.length,
                separatorBuilder: (_, __) => const SizedBox(height: AtlasSpace.s500),
                itemBuilder: (_, i) => _OpportunityCard(
                  opportunity: data[i],
                  onClaim: () => _claim(data[i]),
                ),
              ),
            );
          },
        ),
      ),
    );
  }

  Future<void> _claim(_WinnerOpportunity opp) async {
    try {
      await ref.read(winnersApiProvider).claimPrize(
            drawId: opp.drawId,
            ticketId: opp.ticketId,
          );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Claim received for ticket #${opp.ticketNumber}')),
      );
      await _refresh();
    } on DioException catch (exc) {
      if (!mounted) return;
      final message = _extractError(exc, fallback: 'Claim failed.');
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
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
}

class _WinnerOpportunity {
  const _WinnerOpportunity({
    required this.drawId,
    required this.ticketId,
    required this.ticketNumber,
    required this.isPrimary,
    required this.position,
    required this.contactStatus,
  });

  final String drawId;
  final String ticketId;
  final int ticketNumber;
  final bool isPrimary;
  final int position;
  final String contactStatus;

  bool get canClaim => contactStatus == 'pending';
}

class _OpportunityCard extends StatelessWidget {
  const _OpportunityCard({required this.opportunity, required this.onClaim});

  final _WinnerOpportunity opportunity;
  final VoidCallback onClaim;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(AtlasSpace.s500),
      decoration: BoxDecoration(
        color: AtlasColors.surfaceElevated,
        border: Border.all(
          color: opportunity.isPrimary
              ? AtlasColors.brandPrimary
              : AtlasColors.dividerHairline,
          width: opportunity.isPrimary ? 2 : 1,
        ),
        borderRadius: BorderRadius.circular(AtlasSpace.s300),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            opportunity.isPrimary
                ? 'You won'
                : 'Reserve #${opportunity.position}',
            style: AtlasType.displaySection.copyWith(
              color: opportunity.isPrimary
                  ? AtlasColors.brandPrimary
                  : AtlasColors.textPrimary,
            ),
          ),
          const SizedBox(height: AtlasSpace.s200),
          Text(
            'Ticket #${opportunity.ticketNumber}',
            style: AtlasType.bodyEmphasis,
          ),
          const SizedBox(height: AtlasSpace.s300),
          Text(
            'Status: ${opportunity.contactStatus}',
            style: AtlasType.bodyDefault.copyWith(color: AtlasColors.textSecondary),
          ),
          const SizedBox(height: AtlasSpace.s400),
          if (opportunity.canClaim)
            FilledButton(onPressed: onClaim, child: const Text('Claim prize'))
          else
            Text(
              opportunity.contactStatus == 'claimed'
                  ? 'Claim received. We will be in touch.'
                  : 'This claim has ${opportunity.contactStatus}.',
              style: AtlasType.bodyDefault.copyWith(color: AtlasColors.stateSuccess),
            ),
        ],
      ),
    );
  }
}

class _EmptyState extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AtlasSpace.s800),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.emoji_events_outlined,
                color: AtlasColors.textSecondary, size: 64),
            const SizedBox(height: AtlasSpace.s400),
            Text('No wins yet', style: AtlasType.displaySection),
            const SizedBox(height: AtlasSpace.s300),
            Text(
              'Wins appear here once a draw you entered is revealed. Enter an active draw to be in the running.',
              textAlign: TextAlign.center,
              style: AtlasType.bodyDefault.copyWith(color: AtlasColors.textSecondary),
            ),
          ],
        ),
      ),
    );
  }
}

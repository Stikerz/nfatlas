import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../design/components/nav_bar.dart';
import '../../design/tokens/colours.dart';
import '../../design/tokens/spacing.dart';
import '../../design/tokens/typography.dart';
import '../draws/draws_api.dart';
import '../identity/identity_controller.dart';
import '../identity/register_screen.dart';
import '../skill/skill_question_screen.dart';
import '../tickets/tickets_api.dart';
import '../wallet/wallet_api.dart';
import '../winners/winner_claim_screen.dart';

/// Home shell — tabs render distinct feature panels in-place.
///
/// W7 Day 3 wires: Home (wallet chip + featured active draw), Draws
/// (list of open draws), Tickets (list of my tickets). Account tab
/// stays a placeholder until W7 Day 5 winner-claim + self-exclude UX.
class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  int _tabIndex = 0;

  Future<void> _signOut() async {
    await ref.read(identityControllerProvider.notifier).signOut();
    if (!mounted) return;
    Navigator.of(context).pushAndRemoveUntil<void>(
      MaterialPageRoute<void>(builder: (_) => const RegisterScreen()),
      (_) => false,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Atlas', style: AtlasType.displayCard),
        backgroundColor: AtlasColors.surfaceBase,
        elevation: 0,
        actions: [
          const _WalletChip(),
          IconButton(
            icon: const Icon(Icons.logout),
            color: AtlasColors.textPrimary,
            tooltip: 'Sign out',
            onPressed: _signOut,
          ),
        ],
      ),
      body: SafeArea(child: _panelFor(_tabIndex)),
      bottomNavigationBar: AtlasBottomNav(
        currentIndex: _tabIndex,
        onTap: (i) => setState(() => _tabIndex = i),
        items: const [
          AtlasBottomNavItem(icon: Icons.home_outlined, label: 'HOME'),
          AtlasBottomNavItem(icon: Icons.emoji_events_outlined, label: 'DRAWS'),
          AtlasBottomNavItem(
              icon: Icons.confirmation_number_outlined, label: 'TICKETS'),
          AtlasBottomNavItem(icon: Icons.person_outline, label: 'ACCOUNT'),
        ],
      ),
    );
  }

  Widget _panelFor(int i) {
    switch (i) {
      case 0:
        return const _HomePanel();
      case 1:
        return const _DrawsPanel();
      case 2:
        return const _TicketsPanel();
      default:
        return const _AccountPanel();
    }
  }
}

/// AppBar-embedded balance chip. Pulls balance via wallet_api on first
/// build; renders a skeleton while the request is in flight.
class _WalletChip extends ConsumerWidget {
  const _WalletChip();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(walletBalanceProvider);
    final label = async.when(
      data: (b) => b.formatted,
      loading: () => '…',
      error: (_, __) => '—',
    );
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: AtlasSpace.s200),
      child: Center(
        child: Container(
          padding: const EdgeInsets.symmetric(
            horizontal: AtlasSpace.s300,
            vertical: AtlasSpace.s100,
          ),
          decoration: BoxDecoration(
            color: AtlasColors.brandAccent.withOpacity(0.14),
            borderRadius: BorderRadius.circular(999),
          ),
          child: Text(
            label,
            style: AtlasType.bodyEmphasis.copyWith(
              color: AtlasColors.brandPrimary,
            ),
          ),
        ),
      ),
    );
  }
}

class _HomePanel extends ConsumerWidget {
  const _HomePanel();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(activeDrawsProvider);
    return Padding(
      padding: const EdgeInsets.all(AtlasSpace.s600),
      child: async.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, _) => _ErrorPanel(message: 'Could not load active draw: $err'),
        data: (draws) {
          if (draws.isEmpty) {
            return _EmptyPanel(
              title: 'No active draw',
              body: 'The next draw will appear here as soon as the operator opens it.',
            );
          }
          return _DrawCard(draw: draws.first, primary: true);
        },
      ),
    );
  }
}

class _DrawsPanel extends ConsumerWidget {
  const _DrawsPanel();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(activeDrawsProvider);
    return async.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (err, _) => _ErrorPanel(message: 'Could not load draws: $err'),
      data: (draws) {
        if (draws.isEmpty) {
          return _EmptyPanel(
            title: 'No draws right now',
            body: 'Check back after the next commit-reveal cycle.',
          );
        }
        return ListView.separated(
          padding: const EdgeInsets.all(AtlasSpace.s600),
          itemCount: draws.length,
          separatorBuilder: (_, __) => const SizedBox(height: AtlasSpace.s400),
          itemBuilder: (_, i) => _DrawCard(draw: draws[i]),
        );
      },
    );
  }
}

class _TicketsPanel extends ConsumerWidget {
  const _TicketsPanel();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(myTicketsProvider);
    return async.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (err, _) => _ErrorPanel(message: 'Could not load tickets: $err'),
      data: (tickets) {
        if (tickets.isEmpty) {
          return _EmptyPanel(
            title: 'No tickets yet',
            body: 'Enter an active draw to get your first ticket.',
          );
        }
        return ListView.separated(
          padding: const EdgeInsets.all(AtlasSpace.s600),
          itemCount: tickets.length,
          separatorBuilder: (_, __) => const Divider(height: AtlasSpace.s600),
          itemBuilder: (_, i) => _TicketRow(ticket: tickets[i]),
        );
      },
    );
  }
}

class _AccountPanel extends StatelessWidget {
  const _AccountPanel();

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(AtlasSpace.s600),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            'Account',
            style: AtlasType.displaySection.copyWith(
              color: AtlasColors.brandPrimary,
            ),
          ),
          const SizedBox(height: AtlasSpace.s600),
          Card(
            color: AtlasColors.surfaceElevated,
            elevation: 0,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(AtlasSpace.s300),
              side: BorderSide(color: AtlasColors.dividerHairline),
            ),
            child: ListTile(
              leading: Icon(Icons.emoji_events_outlined,
                  color: AtlasColors.brandPrimary),
              title: const Text('Your wins'),
              subtitle: const Text('Claim any prize you have won'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () => Navigator.of(context).push<void>(
                MaterialPageRoute<void>(
                  builder: (_) => const WinnerClaimScreen(),
                ),
              ),
            ),
          ),
          const SizedBox(height: AtlasSpace.s400),
          Text(
            'Self-exclusion + profile settings land in V1.',
            textAlign: TextAlign.center,
            style: AtlasType.bodySmall.copyWith(
              color: AtlasColors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }
}

class _DrawCard extends StatelessWidget {
  const _DrawCard({required this.draw, this.primary = false});

  final DrawSummary draw;
  final bool primary;

  @override
  Widget build(BuildContext context) {
    final priceMajor = (draw.ticketPriceMinor / 100).toStringAsFixed(2);
    final closeIn = draw.closeTime.difference(DateTime.now().toUtc());
    final closeLabel = closeIn.isNegative
        ? 'closed'
        : 'closes in ${_humanDelta(closeIn)}';
    final canEnter = draw.state == 'sales_open';

    return InkWell(
      onTap: canEnter
          ? () => Navigator.of(context).push<void>(
                MaterialPageRoute<void>(
                  builder: (_) => SkillQuestionScreen(draw: draw),
                ),
              )
          : null,
      borderRadius: BorderRadius.circular(AtlasSpace.s300),
      child: Container(
      padding: const EdgeInsets.all(AtlasSpace.s500),
      decoration: BoxDecoration(
        color: AtlasColors.surfaceElevated,
        borderRadius: BorderRadius.circular(AtlasSpace.s300),
        border: Border.all(
          color: primary
              ? AtlasColors.brandPrimary
              : AtlasColors.dividerHairline,
          width: primary ? 2 : 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            draw.prizeCopy,
            style: primary ? AtlasType.displaySection : AtlasType.displayCard,
          ),
          const SizedBox(height: AtlasSpace.s200),
          Row(
            children: [
              Text(
                '${draw.currency == 'NGN' ? '₦' : ''}$priceMajor',
                style: AtlasType.bodyEmphasis.copyWith(
                  color: AtlasColors.brandPrimary,
                ),
              ),
              const SizedBox(width: AtlasSpace.s300),
              Text(
                closeLabel,
                style: AtlasType.bodyDefault.copyWith(
                  color: AtlasColors.textSecondary,
                ),
              ),
            ],
          ),
          const SizedBox(height: AtlasSpace.s400),
          Text(
            'Commitment ${draw.commitment.substring(0, 12)}…${draw.commitment.substring(draw.commitment.length - 12)}',
            style: AtlasType.bodyMono.copyWith(
              color: AtlasColors.textSecondary,
              fontSize: 12,
            ),
          ),
          if (canEnter) ...[
            const SizedBox(height: AtlasSpace.s400),
            Text(
              'TAP TO ENTER →',
              style: AtlasType.bodySmall.copyWith(
                color: AtlasColors.brandPrimary,
              ),
            ),
          ],
        ],
      ),
    ),
    );
  }

  String _humanDelta(Duration d) {
    if (d.inDays > 1) return '${d.inDays}d';
    if (d.inHours > 1) return '${d.inHours}h';
    if (d.inMinutes > 1) return '${d.inMinutes}m';
    return '${d.inSeconds}s';
  }
}

class _TicketRow extends StatelessWidget {
  const _TicketRow({required this.ticket});

  final TicketSummary ticket;

  @override
  Widget build(BuildContext context) {
    final issued = DateFormat('yyyy-MM-dd HH:mm').format(ticket.issuedAt.toLocal());
    final isFree = ticket.entrySource == 'free';
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.symmetric(
            horizontal: AtlasSpace.s300,
            vertical: AtlasSpace.s100,
          ),
          decoration: BoxDecoration(
            color: isFree
                ? AtlasColors.brandAccent.withOpacity(0.14)
                : AtlasColors.brandPrimary.withOpacity(0.14),
            borderRadius: BorderRadius.circular(AtlasSpace.s100),
          ),
          child: Text(
            isFree ? 'FREE' : 'PAID',
            style: AtlasType.bodySmall.copyWith(
              color: isFree ? AtlasColors.brandAccent : AtlasColors.brandPrimary,
            ),
          ),
        ),
        const SizedBox(width: AtlasSpace.s400),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Ticket #${ticket.ticketNumber}',
                style: AtlasType.bodyEmphasis,
              ),
              Text(
                'Issued $issued',
                style: AtlasType.bodySmall.copyWith(
                  color: AtlasColors.textSecondary,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _EmptyPanel extends StatelessWidget {
  const _EmptyPanel({required this.title, required this.body});

  final String title;
  final String body;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AtlasSpace.s800),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              title,
              style: AtlasType.displaySection.copyWith(
                color: AtlasColors.brandPrimary,
              ),
            ),
            const SizedBox(height: AtlasSpace.s400),
            Text(
              body,
              textAlign: TextAlign.center,
              style: AtlasType.bodyDefault.copyWith(
                color: AtlasColors.textSecondary,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ErrorPanel extends StatelessWidget {
  const _ErrorPanel({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AtlasSpace.s800),
        child: Text(
          message,
          textAlign: TextAlign.center,
          style: AtlasType.bodyDefault.copyWith(
            color: AtlasColors.brandPrimary,
          ),
        ),
      ),
    );
  }
}

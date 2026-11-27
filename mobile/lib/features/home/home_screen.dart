import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../design/components/nav_bar.dart';
import '../../design/tokens/colours.dart';
import '../../design/tokens/spacing.dart';
import '../../design/tokens/typography.dart';
import '../draws/draws_api.dart';
import '../account/self_exclusion_screen.dart';
import '../identity/identity_controller.dart';
import '../identity/register_screen.dart';
import '../tickets/entry_purchase_screen.dart';
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
            icon: Icons.confirmation_number_outlined,
            label: 'TICKETS',
          ),
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
            color: AtlasColors.brandAccent.withValues(alpha: 0.14),
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
            return const _EmptyPanel(
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
          return const _EmptyPanel(
            title: 'No draws right now',
            body: 'Check back after the next commit-reveal cycle.',
          );
        }
        return _DrawCarousel(draws: draws);
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
          return const _EmptyPanel(
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

class _AccountPanel extends ConsumerWidget {
  const _AccountPanel();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final userId = ref.watch(identityControllerProvider).userId;
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
              side: const BorderSide(color: AtlasColors.dividerHairline),
            ),
            child: ListTile(
              leading: const Icon(
                Icons.emoji_events_outlined,
                color: AtlasColors.brandPrimary,
              ),
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
          // ADR-010 Phase A. Deliberately a plain, unstyled text button at
          // the bottom of the panel: a closure control should be findable
          // without being promoted. No confirmation happens here — the
          // screen states the limits first, then asks for a typed
          // confirmation and an OTP.
          if (userId != null)
            TextButton(
              onPressed: () => Navigator.of(context).push<void>(
                MaterialPageRoute<void>(
                  builder: (_) => SelfExclusionScreen(userId: userId),
                ),
              ),
              child: Text(
                'Close my account',
                style: AtlasType.bodySmall.copyWith(
                  color: AtlasColors.textSecondary,
                  decoration: TextDecoration.underline,
                ),
              ),
            ),
          const SizedBox(height: AtlasSpace.s200),
          Text(
            'Profile settings land in V1.',
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

/// Horizontally swipeable browser for concurrent draws.
///
/// Replaces a vertical `ListView` (2026-11-27). Draws arrive ordered by
/// `close_time` ascending from `draw_service.list_active`, so the one
/// closing soonest is first — the order is now visible to the user, which
/// it was not in a scrolling list, so it had better stay meaningful.
///
/// Two deliberate accessibility choices, because a swipe-only surface is
/// easy to get wrong:
///
///  - The page indicator dots are **tappable**, not decorative. Swipe is
///    not the only way to move between draws.
///  - Each page is wrapped in a `Semantics` node announcing its position
///    ("draw 2 of 3"), so a screen-reader user knows more draws exist.
///    A bare PageView gives no such signal.
///
/// With a single draw the indicator is hidden entirely — dots that cannot
/// move are noise.
class _DrawCarousel extends StatefulWidget {
  const _DrawCarousel({required this.draws});

  final List<DrawSummary> draws;

  @override
  State<_DrawCarousel> createState() => _DrawCarouselState();
}

class _DrawCarouselState extends State<_DrawCarousel> {
  late final PageController _controller;
  int _page = 0;

  @override
  void initState() {
    super.initState();
    // viewportFraction < 1 leaves the neighbouring card peeking, which is
    // the affordance that tells a user there is something to swipe to.
    // Without it a carousel reads as a single static card.
    _controller = PageController(viewportFraction: 0.88);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _goTo(int i) => _controller.animateToPage(
        i,
        duration: const Duration(milliseconds: 280),
        curve: Curves.easeOutCubic,
      );

  @override
  Widget build(BuildContext context) {
    final draws = widget.draws;
    final multiple = draws.length > 1;

    return Column(
      children: [
        const SizedBox(height: AtlasSpace.s500),
        // Names the ordering rather than the quantity. Wireframe 16 §3.1:
        // a count is inventory language ("94% sold!"), which tone-doc
        // Anchor 1 rejects — and it is redundant, since the dots say
        // "three" and the Semantics labels say "of 3". The organising
        // principle is the thing the dots cannot communicate.
        if (multiple)
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: AtlasSpace.s600),
            child: Align(
              alignment: Alignment.centerLeft,
              child: Text(
                'Closing soonest first',
                style: AtlasType.bodySmall.copyWith(
                  color: AtlasColors.textSecondary,
                ),
              ),
            ),
          ),
        if (multiple) const SizedBox(height: AtlasSpace.s300),
        Expanded(
          child: PageView.builder(
            controller: _controller,
            itemCount: draws.length,
            onPageChanged: (i) => setState(() => _page = i),
            itemBuilder: (_, i) => Semantics(
              label: multiple ? 'Draw ${i + 1} of ${draws.length}' : null,
              child: Padding(
                padding: const EdgeInsets.only(
                  left: AtlasSpace.s300,
                  right: AtlasSpace.s300,
                  bottom: AtlasSpace.s600,
                ),
                child: SingleChildScrollView(
                  // NOT `primary: i == _page`. Wireframe 16 §3.2: on Home
                  // the bordered treatment means "the featured draw"; reusing
                  // it here to mean "the page you are on" gives one visual
                  // two meanings across two screens. Being centred, with the
                  // neighbours cropped and the dot filled, already says which
                  // page is active.
                  child: _DrawCard(draw: draws[i]),
                ),
              ),
            ),
          ),
        ),
        if (multiple)
          Padding(
            padding: const EdgeInsets.only(bottom: AtlasSpace.s600),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                for (var i = 0; i < draws.length; i++)
                  Semantics(
                    button: true,
                    selected: i == _page,
                    label: 'Go to draw ${i + 1} of ${draws.length}',
                    child: InkWell(
                      onTap: () => _goTo(i),
                      customBorder: const CircleBorder(),
                      // 44pt minimum touch target around an 8pt dot.
                      child: SizedBox(
                        width: 44,
                        height: 44,
                        child: Center(
                          child: AnimatedContainer(
                            duration: const Duration(milliseconds: 200),
                            width: i == _page ? 24 : 8,
                            height: 8,
                            decoration: BoxDecoration(
                              color: i == _page
                                  ? AtlasColors.brandPrimary
                                  : AtlasColors.dividerStrong,
                              borderRadius: BorderRadius.circular(4),
                            ),
                          ),
                        ),
                      ),
                    ),
                  ),
              ],
            ),
          ),
      ],
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
                  builder: (_) => EntryPurchaseScreen(draw: draw),
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
                ? AtlasColors.brandAccent.withValues(alpha: 0.14)
                : AtlasColors.brandPrimary.withValues(alpha: 0.14),
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

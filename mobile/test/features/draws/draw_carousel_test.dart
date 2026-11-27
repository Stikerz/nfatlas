import 'package:atlas_mobile/design/atlas_theme.dart';
import 'package:atlas_mobile/features/draws/draws_api.dart';
import 'package:atlas_mobile/features/home/home_screen.dart';
import 'package:atlas_mobile/features/identity/identity_api.dart';
import 'package:atlas_mobile/features/identity/identity_controller.dart';
import 'package:atlas_mobile/features/tickets/tickets_api.dart';
import 'package:atlas_mobile/features/wallet/wallet_api.dart';
import 'package:atlas_mobile/services/session_storage.dart';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

/// The Draws tab browses concurrent draws by swiping (2026-11-27).
///
/// What matters here is not that a PageView exists — it is that a user who
/// cannot or will not swipe can still reach every draw, and that a screen
/// reader announces there is more than one. A carousel that only responds
/// to a horizontal drag silently hides inventory from part of the audience.
///
/// Draws arrive ordered by `close_time` ascending from the backend
/// (`draw_service.list_active`). The carousel makes that order visible, so
/// these tests pin it.

DrawSummary _draw({
  required String id,
  required String prize,
  required DateTime closeTime,
  int priceMinor = 50000,
}) {
  return DrawSummary(
    id: id,
    prizeCopy: prize,
    ticketPriceMinor: priceMinor,
    currency: 'NGN',
    closeTime: closeTime,
    drawTime: closeTime.add(const Duration(hours: 1)),
    state: 'sales_open',
    commitment:
        '40bc109598f824780aad5502b60253eea5d3328ddc676a2a07149a731adbac3f',
  );
}

final _soonest = _draw(
  id: 'draw-1',
  prize: 'Win a Toyota Corolla 2026, insured and delivered.',
  closeTime: DateTime.utc(2026, 12, 1, 12),
  priceMinor: 25000,
);
final _middle = _draw(
  id: 'draw-2',
  prize: 'Win NGN 2,000,000 cash or a mortgage-free Lagos apartment.',
  closeTime: DateTime.utc(2026, 12, 5, 12),
);
final _latest = _draw(
  id: 'draw-3',
  prize: 'Win NGN 5,000,000 cash, paid within 48 hours.',
  closeTime: DateTime.utc(2026, 12, 9, 12),
  priceMinor: 100000,
);

Widget _host(List<DrawSummary> draws) {
  return ProviderScope(
    overrides: [
      identityControllerProvider.overrideWith(
        (ref) => IdentityController(IdentityApi(Dio()), SessionStorage()),
      ),
      walletBalanceProvider.overrideWith(
        (ref) async => WalletBalance(
          balanceMinor: 0,
          currency: 'NGN',
          updatedAt: DateTime.utc(2026, 11, 27),
        ),
      ),
      activeDrawsProvider.overrideWith((ref) async => draws),
      myTicketsProvider.overrideWith((ref) async => <TicketSummary>[]),
    ],
    child: MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: atlasTheme(),
      home: const HomeScreen(),
    ),
  );
}

/// Home opens on the Home tab; the carousel lives on Draws.
Future<void> _openDrawsTab(WidgetTester tester) async {
  await tester.pumpAndSettle();
  await tester.tap(find.text('DRAWS'));
  await tester.pumpAndSettle();
}

void main() {
  testWidgets('names the ordering rather than the quantity', (tester) async {
    tester.view.physicalSize = const Size(402, 874);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.reset);

    await tester.pumpWidget(_host([_soonest, _middle, _latest]));
    await _openDrawsTab(tester);

    // Wireframe 16 §3.1: a count is inventory language and is redundant
    // beside the dots. The label names the organising principle instead.
    expect(find.text('Closing soonest first'), findsOneWidget);
    expect(find.text('3 draws open'), findsNothing);
  });

  testWidgets('opens on the draw closing soonest', (tester) async {
    tester.view.physicalSize = const Size(402, 874);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.reset);

    await tester.pumpWidget(_host([_soonest, _middle, _latest]));
    await _openDrawsTab(tester);

    // Backend orders by close_time ascending. The first page must be the
    // most urgent one, not an arbitrary member of the list.
    expect(find.text(_soonest.prizeCopy), findsOneWidget);
  });

  testWidgets('swiping reaches the next draw', (tester) async {
    tester.view.physicalSize = const Size(402, 874);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.reset);

    await tester.pumpWidget(_host([_soonest, _middle, _latest]));
    await _openDrawsTab(tester);

    await tester.drag(find.byType(PageView), const Offset(-400, 0));
    await tester.pumpAndSettle();

    expect(find.text(_middle.prizeCopy), findsOneWidget);
  });

  testWidgets(
    'every draw is reachable WITHOUT swiping, via the page indicator',
    (tester) async {
      tester.view.physicalSize = const Size(402, 874);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.reset);

      await tester.pumpWidget(_host([_soonest, _middle, _latest]));
      await _openDrawsTab(tester);

      // The accessibility contract: the dots are controls, not decoration.
      // If this fails, a user who cannot perform a horizontal drag can only
      // ever see the first draw.
      await tester.tap(find.bySemanticsLabel('Go to draw 3 of 3'));
      await tester.pumpAndSettle();

      expect(find.text(_latest.prizeCopy), findsOneWidget);
    },
  );

  testWidgets('announces position to a screen reader', (tester) async {
    tester.view.physicalSize = const Size(402, 874);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.reset);
    final handle = tester.ensureSemantics();

    await tester.pumpWidget(_host([_soonest, _middle, _latest]));
    await _openDrawsTab(tester);

    // Without this a bare PageView gives no signal that more draws exist.
    expect(find.bySemanticsLabel('Draw 1 of 3'), findsOneWidget);

    handle.dispose();
  });

  testWidgets('a single draw shows no indicator and no count', (tester) async {
    tester.view.physicalSize = const Size(402, 874);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.reset);

    await tester.pumpWidget(_host([_soonest]));
    await _openDrawsTab(tester);

    // Dots that cannot move are noise, and "1 draws open" is wrong anyway.
    expect(find.text('Closing soonest first'), findsNothing);
    expect(find.bySemanticsLabel('Go to draw 1 of 1'), findsNothing);
    expect(find.text(_soonest.prizeCopy), findsOneWidget);
  });

  testWidgets('empty state survives', (tester) async {
    tester.view.physicalSize = const Size(402, 874);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.reset);

    await tester.pumpWidget(_host(<DrawSummary>[]));
    await _openDrawsTab(tester);

    expect(find.text('No draws right now'), findsOneWidget);
  });
}

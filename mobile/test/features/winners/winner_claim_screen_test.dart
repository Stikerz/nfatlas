import 'package:atlas_mobile/features/tickets/tickets_api.dart';
import 'package:atlas_mobile/features/winners/winner_claim_screen.dart';
import 'package:atlas_mobile/features/winners/winners_api.dart';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

/// WinnerClaimScreen renders the ticket × draw_winners intersection.
///
/// The trust-story requirement: a user who owns a winning ticket must see
/// the Claim CTA; a user who does not own a winning ticket must see the
/// empty state; a claim already 'claimed' must NOT re-expose the button.
class _FakeTicketsApi extends TicketsApi {
  _FakeTicketsApi(this._tickets) : super(Dio());

  final List<TicketSummary> _tickets;

  @override
  Future<List<TicketSummary>> listMine() async => _tickets;
}

class _FakeWinnersApi extends WinnersApi {
  _FakeWinnersApi(this._winnersByDraw) : super(Dio());

  final Map<String, List<WinnerSummary>> _winnersByDraw;

  @override
  Future<List<WinnerSummary>> listForDraw(String drawId) async =>
      _winnersByDraw[drawId] ?? const [];
}

TicketSummary _ticket({
  required String id,
  required String drawId,
  int number = 1,
}) {
  return TicketSummary(
    id: id,
    drawId: drawId,
    ticketNumber: number,
    entrySource: 'paid',
    issuedAt: DateTime.utc(2026, 8, 1, 12),
  );
}

WinnerSummary _winner({
  required String ticketId,
  int position = 0,
  bool isPrimary = true,
  String contactStatus = 'pending',
}) {
  return WinnerSummary(
    position: position,
    isPrimary: isPrimary,
    ticketId: ticketId,
    userId: 'user-under-test',
    contactStatus: contactStatus,
  );
}

Widget _host({
  required List<TicketSummary> tickets,
  required Map<String, List<WinnerSummary>> winnersByDraw,
}) {
  return ProviderScope(
    overrides: [
      ticketsApiProvider.overrideWithValue(_FakeTicketsApi(tickets)),
      winnersApiProvider.overrideWithValue(_FakeWinnersApi(winnersByDraw)),
    ],
    child: const MaterialApp(home: WinnerClaimScreen()),
  );
}

void main() {
  testWidgets('empty when the user owns no tickets', (tester) async {
    await tester.pumpWidget(_host(tickets: [], winnersByDraw: {}));
    await tester.pumpAndSettle();

    expect(find.text('No wins yet'), findsOneWidget);
    expect(find.text('Claim prize'), findsNothing);
  });

  testWidgets('empty when tickets exist but user is not on the winners list',
      (tester) async {
    await tester.pumpWidget(
      _host(
        tickets: [_ticket(id: 't1', drawId: 'd1')],
        winnersByDraw: {
          'd1': [_winner(ticketId: 'someone-else')],
        },
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('No wins yet'), findsOneWidget);
    expect(find.text('Claim prize'), findsNothing);
  });

  testWidgets('primary winner sees the "You won" card + Claim button',
      (tester) async {
    await tester.pumpWidget(
      _host(
        tickets: [_ticket(id: 't1', drawId: 'd1', number: 42)],
        winnersByDraw: {
          'd1': [_winner(ticketId: 't1', isPrimary: true, position: 0)],
        },
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('You won'), findsOneWidget);
    expect(find.text('Ticket #42'), findsOneWidget);
    expect(find.text('Claim prize'), findsOneWidget);
  });

  testWidgets('reserve winner sees "Reserve #N" instead of "You won"',
      (tester) async {
    await tester.pumpWidget(
      _host(
        tickets: [_ticket(id: 't1', drawId: 'd1')],
        winnersByDraw: {
          'd1': [_winner(ticketId: 't1', isPrimary: false, position: 3)],
        },
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Reserve #3'), findsOneWidget);
    expect(find.text('You won'), findsNothing);
    expect(find.text('Claim prize'), findsOneWidget);
  });

  testWidgets('already-claimed row hides the Claim button', (tester) async {
    await tester.pumpWidget(
      _host(
        tickets: [_ticket(id: 't1', drawId: 'd1')],
        winnersByDraw: {
          'd1': [
            _winner(
              ticketId: 't1',
              isPrimary: true,
              contactStatus: 'claimed',
            ),
          ],
        },
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('You won'), findsOneWidget);
    expect(find.text('Claim prize'), findsNothing);
    expect(
      find.text('Claim received. We will be in touch.'),
      findsOneWidget,
    );
  });

  testWidgets('a failing winners lookup does NOT crash the screen',
      (tester) async {
    // Simulates a draw that hasn't been revealed yet — winners_api throws.
    final failingWinners = _FakeWinnersApiThrowing();
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          ticketsApiProvider.overrideWithValue(
            _FakeTicketsApi([_ticket(id: 't1', drawId: 'd1')]),
          ),
          winnersApiProvider.overrideWithValue(failingWinners),
        ],
        child: const MaterialApp(home: WinnerClaimScreen()),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('No wins yet'), findsOneWidget);
  });
}

class _FakeWinnersApiThrowing extends WinnersApi {
  _FakeWinnersApiThrowing() : super(Dio());

  @override
  Future<List<WinnerSummary>> listForDraw(String drawId) async {
    throw DioException(requestOptions: RequestOptions(path: '/winners'));
  }
}

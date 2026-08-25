// Golden captures for every consumer screen.
//
// Purpose is visual review, not pixel regression: the goldens are committed so
// a reviewer can see what each screen looks like without booting a simulator,
// and so a UI change shows up as an image diff in the pull request.
//
// Refresh after an intentional change:
//
//     flutter test test/design/screen_goldens_test.dart --update-goldens
//
// These render real typography because the faces are bundled under
// assets/google_fonts/ rather than fetched at runtime — see main.dart. Loading
// them here is what `loadAppFonts` does; without it Flutter's test binding
// substitutes Ahem and every glyph is a filled box.
import 'package:atlas_mobile/design/tokens/typography.dart';
import 'package:atlas_mobile/features/draws/draws_api.dart';
import 'package:atlas_mobile/features/tickets/tickets_api.dart';
import 'package:atlas_mobile/features/wallet/wallet_api.dart';
import 'package:atlas_mobile/features/home/home_screen.dart';
import 'package:atlas_mobile/features/identity/identity_api.dart';
import 'package:atlas_mobile/features/identity/identity_controller.dart';
import 'package:atlas_mobile/features/identity/otp_screen.dart';
import 'package:atlas_mobile/features/identity/password_screen.dart';
import 'package:atlas_mobile/features/identity/register_screen.dart';
import 'package:atlas_mobile/features/identity/welcome_screen.dart';
import 'package:atlas_mobile/features/skill/skill_question_screen.dart';
import 'package:atlas_mobile/features/winners/winner_claim_screen.dart';
import 'package:atlas_mobile/services/session_storage.dart';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:google_fonts/google_fonts.dart';

/// Loads the bundled faces so goldens render real typography rather than the
/// Ahem placeholder, where every glyph is a filled box.
///
/// Uses google_fonts' own preload rather than a hand-rolled FontLoader:
/// it resolves the family-and-variant naming internally. Registering the
/// families by filename instead silently misses JetBrainsMono, and the only
/// symptom is the commitment hash rendering as blocks.
Future<void> _loadAppFonts() async {
  // Touch every style the screens use so each queues a load...
  AtlasType.displayHero;
  AtlasType.displaySection;
  AtlasType.displayDraw;
  AtlasType.displayCard;
  AtlasType.bodyDefault;
  AtlasType.bodyEmphasis;
  AtlasType.bodySmall;
  AtlasType.bodyButton;
  AtlasType.labelMicro;
  AtlasType.bodyMono;
  // ...then wait for all of them.
  await GoogleFonts.pendingFonts();

  // Flutter ships MaterialIcons but the test binding does not register it, so
  // every Icon would otherwise paint as an empty box.
  await (FontLoader('MaterialIcons')
        ..addFont(rootBundle.load('fonts/MaterialIcons-Regular.otf')))
      .load();
}

Widget _host(Widget screen) {
  return ProviderScope(
    overrides: [
      // Real controller over a bare Dio: constructed but never driven, since
      // these tests only paint. Mirrors the harness the other widget tests use.
      identityControllerProvider.overrideWith(
        (ref) => IdentityController(IdentityApi(Dio()), SessionStorage()),
      ),
      // Home fetches wallet, draws and tickets on build. Without these it
      // paints a spinner forever, which is a useless thing to review — the
      // point of the golden is to show the populated screen.
      walletBalanceProvider.overrideWith((ref) async => _wallet),
      activeDrawsProvider.overrideWith((ref) async => <DrawSummary>[_draw]),
      myTicketsProvider.overrideWith((ref) async => <TicketSummary>[_ticket]),
    ],
    child: MaterialApp(debugShowCheckedModeBanner: false, home: screen),
  );
}

final _wallet = WalletBalance(
  balanceMinor: 250000,
  currency: 'NGN',
  updatedAt: DateTime.utc(2026, 8, 25, 12, 0),
);

final _ticket = TicketSummary(
  id: '209e6413-9a03-4b1e-9f2c-0190c6ff45c5',
  drawId: '01919abc-0d6a-7000-8000-000000000001',
  ticketNumber: 142,
  entrySource: 'paid',
  issuedAt: DateTime.utc(2026, 8, 25, 11, 42),
);

/// Fixed so the goldens are deterministic — a live draw would change the
/// rendered close time on every run and make every golden dirty.
final _draw = DrawSummary(
  id: '01919abc-0d6a-7000-8000-000000000001',
  prizeCopy: 'Win ₦2,000,000 cash or a mortgage-free Lagos apartment.',
  ticketPriceMinor: 50000,
  currency: 'NGN',
  closeTime: DateTime.utc(2026, 8, 28, 13, 5),
  drawTime: DateTime.utc(2026, 8, 28, 14, 5),
  state: 'sales_open',
  commitment:
      '40bc109598f824780aad5502b60253eea5d3328ddc676a2a07149a731adbac3f',
);

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUpAll(() async {
    // Belt and braces: main() sets this too, but goldens never call main().
    GoogleFonts.config.allowRuntimeFetching = false;
    await _loadAppFonts();
  });

  final screens = <String, Widget Function()>{
    'register': () => const RegisterScreen(),
    'otp': () => const OtpScreen(),
    'password': () => const PasswordScreen(),
    'welcome': () => const WelcomeScreen(),
    'home': () => const HomeScreen(),
    'skill-question': () => SkillQuestionScreen(draw: _draw),
    'winner-claim': () => const WinnerClaimScreen(),
  };

  screens.forEach((name, build) {
    testWidgets('golden: $name', (tester) async {
      // iPhone 17 logical size, 1x so the goldens stay a reviewable weight.
      tester.view.physicalSize = const Size(402, 874);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.reset);

      await tester.pumpWidget(_host(build()));
      // Long enough to lay out and settle, short enough that WelcomeScreen's
      // 800ms auto-advance to Home has not fired — otherwise its golden would
      // show the screen it navigates to rather than itself.
      await tester.pump(const Duration(milliseconds: 300));

      await expectLater(
        find.byType(MaterialApp),
        matchesGoldenFile('goldens/$name.png'),
      );

      // Unmount before the test ends. Screens schedule work in initState with
      // a `mounted` guard, so tearing the tree down makes those callbacks
      // no-op; draining afterwards clears the timers the binding would
      // otherwise report as pending.
      await tester.pumpWidget(const SizedBox.shrink());
      await tester.pump(const Duration(seconds: 2));
    });
  });
}

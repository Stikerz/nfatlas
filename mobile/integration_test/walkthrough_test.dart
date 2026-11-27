import 'package:atlas_mobile/main.dart' as app;
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';

/// Capture harness for `docs/VISUAL-WALKTHROUGH.md` — browses the
/// photographed draw carousel on a simulator against the live backend,
/// slowly enough to be watchable on a screen recording.
///
/// This is NOT a regression test. It asserts just enough to fail loudly
/// rather than silently record the wrong thing.
///
/// It does not record a sign-in, because **the app has no sign-in flow**:
/// `identityApi.login` is called in exactly one place, at the end of
/// registration (`identity_controller.submitPassword`), and the "Already
/// have an account? Sign in" text on the registration screen has no tap
/// handler. A returning user whose 8-hour session has lapsed has no route
/// back into their account. Recorded as a gap rather than worked around.
///
/// Run against a stack seeded with draws carrying `prize_image_url`, and
/// with `main.dart` temporarily routed to `HomeScreen`. Both are
/// capture-only changes and are reverted afterwards.
void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  Future<void> beat(WidgetTester tester, [int ms = 1700]) async {
    await tester.pumpAndSettle();
    await tester.runAsync(
      () => Future<void>.delayed(Duration(milliseconds: ms)),
    );
    await tester.pumpAndSettle();
  }

  testWidgets('browse the photographed draws', (tester) async {
    app.main();
    await beat(tester, 2500);

    expect(
      find.text('Closing soonest first'),
      findsOneWidget,
      reason: 'expected the Draws tab carousel',
    );
    expect(
      find.byType(Image),
      findsWidgets,
      reason: 'expected prize photography to be loaded',
    );
    await beat(tester, 2200);

    // Forward through every draw.
    for (var i = 0; i < 3; i++) {
      await tester.drag(find.byType(PageView), const Offset(-380, 0));
      await beat(tester);
    }

    // Back to the first using the page indicator — the route that works
    // without swiping, which is the accessibility contract in wireframe 16.
    await tester.tap(find.bySemanticsLabel(RegExp('Go to draw 1 of')));
    await beat(tester, 2500);
  });
}

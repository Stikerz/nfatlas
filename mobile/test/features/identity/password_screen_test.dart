import 'package:atlas_mobile/design/components/button.dart';
import 'package:atlas_mobile/features/identity/identity_api.dart';
import 'package:atlas_mobile/features/identity/identity_controller.dart';
import 'package:atlas_mobile/features/identity/password_screen.dart';
import 'package:atlas_mobile/services/session_storage.dart';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

/// Password rules per wireframe wf-01 §Screen 1.3:
///   1. 10 characters or more
///   2. Mix of letters and numbers
///   3. "Not one you use for banking" (advisory only, always green)
///
/// The Create-account button must be disabled until rules 1 + 2 are both
/// satisfied. This test never actually POSTs — it validates rule + button
/// state only, which is what the founder walkthrough hinges on.
Widget _host() {
  return ProviderScope(
    overrides: [
      // Real controller + real IdentityApi(Dio()) + real SessionStorage —
      // neither IO'd during construction, and the tests never press submit.
      identityControllerProvider.overrideWith(
        (ref) => IdentityController(IdentityApi(Dio()), SessionStorage()),
      ),
    ],
    child: const MaterialApp(home: PasswordScreen()),
  );
}

AtlasButton _createButton(WidgetTester tester) {
  return tester.widget<AtlasButton>(
    find.byWidgetPredicate(
      (w) => w is AtlasButton && w.label == 'Create account',
    ),
  );
}

Future<void> _typePassword(WidgetTester tester, String value) async {
  await tester.enterText(find.byType(TextField), value);
  await tester.pump();
}

void main() {
  testWidgets('empty password: both rules unsatisfied, button disabled',
      (tester) async {
    await tester.pumpWidget(_host());
    await tester.pumpAndSettle();

    expect(_createButton(tester).onPressed, isNull);
    expect(find.text('10 characters or more'), findsOneWidget);
    expect(find.text('Mix of letters and numbers'), findsOneWidget);
    expect(find.text('Not one you use for banking'), findsOneWidget);
  });

  testWidgets('only letters: mix rule fails, button still disabled',
      (tester) async {
    await tester.pumpWidget(_host());
    await tester.pumpAndSettle();

    await _typePassword(tester, 'lettersonly');

    expect(_createButton(tester).onPressed, isNull);
  });

  testWidgets('only digits: mix rule fails, button still disabled',
      (tester) async {
    await tester.pumpWidget(_host());
    await tester.pumpAndSettle();

    await _typePassword(tester, '1234567890');

    expect(_createButton(tester).onPressed, isNull);
  });

  testWidgets('9 chars with mix: length rule fails, button disabled',
      (tester) async {
    await tester.pumpWidget(_host());
    await tester.pumpAndSettle();

    await _typePassword(tester, 'abc123abc');

    expect(_createButton(tester).onPressed, isNull);
  });

  testWidgets('10 chars with mix: both rules pass, button enabled',
      (tester) async {
    await tester.pumpWidget(_host());
    await tester.pumpAndSettle();

    await _typePassword(tester, 'abc123abc4');

    expect(_createButton(tester).onPressed, isNotNull);
  });

  testWidgets('crossing the threshold re-enables the button', (tester) async {
    await tester.pumpWidget(_host());
    await tester.pumpAndSettle();

    await _typePassword(tester, 'abc12345');
    expect(_createButton(tester).onPressed, isNull);

    await _typePassword(tester, 'abc1234567');
    expect(_createButton(tester).onPressed, isNotNull);

    await _typePassword(tester, 'abc12');
    expect(_createButton(tester).onPressed, isNull);
  });
}

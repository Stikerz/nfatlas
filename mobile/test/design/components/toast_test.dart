import 'package:atlas_mobile/design/components/toast.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

/// AtlasToast contract per _bmad-output/planning-artifacts/design/components.md §16:
/// default and success dismiss on their own; danger stays open longer and
/// exposes a Dismiss action.
Widget _hostWithTrigger(void Function(BuildContext) onTap) {
  return MaterialApp(
    home: Scaffold(
      body: Builder(
        builder: (ctx) => Center(
          child: ElevatedButton(
            onPressed: () => onTap(ctx),
            child: const Text('go'),
          ),
        ),
      ),
    ),
  );
}

void main() {
  testWidgets('default variant shows the message and no dismiss action',
      (tester) async {
    await tester.pumpWidget(
      _hostWithTrigger((ctx) => AtlasToast.show(ctx, message: 'saved')),
    );

    await tester.tap(find.text('go'));
    await tester.pump();

    expect(find.text('saved'), findsOneWidget);
    expect(find.text('Dismiss'), findsNothing);
  });

  testWidgets('success variant renders check icon alongside message',
      (tester) async {
    await tester.pumpWidget(
      _hostWithTrigger(
        (ctx) => AtlasToast.show(
          ctx,
          message: 'linked',
          variant: AtlasToastVariant.success,
        ),
      ),
    );

    await tester.tap(find.text('go'));
    await tester.pump();

    expect(find.text('linked'), findsOneWidget);
    expect(find.byIcon(Icons.check_circle), findsOneWidget);
  });

  testWidgets('danger variant exposes a Dismiss action that clears the toast',
      (tester) async {
    await tester.pumpWidget(
      _hostWithTrigger(
        (ctx) => AtlasToast.show(
          ctx,
          message: 'failed',
          variant: AtlasToastVariant.danger,
        ),
      ),
    );

    await tester.tap(find.text('go'));
    await tester.pumpAndSettle();
    expect(find.text('failed'), findsOneWidget);
    expect(find.text('Dismiss'), findsOneWidget);

    await tester.tap(find.text('Dismiss'));
    await tester.pumpAndSettle();
    expect(find.text('failed'), findsNothing);
  });

  testWidgets('second toast replaces the first (clearSnackBars on show)',
      (tester) async {
    await tester.pumpWidget(
      _hostWithTrigger(
        (ctx) {
          AtlasToast.show(ctx, message: 'first');
          AtlasToast.show(ctx, message: 'second');
        },
      ),
    );

    await tester.tap(find.text('go'));
    await tester.pump();

    expect(find.text('first'), findsNothing);
    expect(find.text('second'), findsOneWidget);
  });
}

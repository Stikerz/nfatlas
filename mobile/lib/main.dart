import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'design/tokens/colours.dart';
import 'design/tokens/spacing.dart';
import 'design/tokens/typography.dart';

/// Day 1 shell — proves tokens compile and the app boots on iOS + Android.
/// Feature modules (identity, home, tickets…) land Days 2-5.
void main() {
  runApp(const ProviderScope(child: AtlasApp()));
}

class AtlasApp extends StatelessWidget {
  const AtlasApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Atlas',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        scaffoldBackgroundColor: AtlasColors.surfaceBase,
        colorScheme: const ColorScheme.light(
          primary: AtlasColors.brandPrimary,
          onPrimary: AtlasColors.textInverted,
          secondary: AtlasColors.brandAccent,
          surface: AtlasColors.surfaceBase,
          onSurface: AtlasColors.textPrimary,
          error: AtlasColors.stateDanger,
        ),
      ),
      home: const _Day1Shell(),
    );
  }
}

class _Day1Shell extends StatelessWidget {
  const _Day1Shell();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(AtlasSpace.s800),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text('Atlas', style: AtlasType.displaySection),
              const SizedBox(height: AtlasSpace.s400),
              Text(
                'Day 1 shell — tokens loaded.',
                style: AtlasType.bodyDefault.copyWith(
                  color: AtlasColors.textSecondary,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

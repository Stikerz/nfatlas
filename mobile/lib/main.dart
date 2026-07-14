import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'design/tokens/colours.dart';
import 'design/tokens/spacing.dart';
import 'design/tokens/typography.dart';
import 'features/home/home_screen.dart';
import 'features/identity/identity_api.dart';
import 'features/identity/register_screen.dart';
import 'services/session_storage.dart';

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
        appBarTheme: const AppBarTheme(
          backgroundColor: AtlasColors.surfaceBase,
          foregroundColor: AtlasColors.textPrimary,
          elevation: 0,
        ),
      ),
      home: const _SplashRouter(),
    );
  }
}

/// Boot check: if a session token is present and /sessions/current returns
/// 200, land in Home; otherwise land in Register.
class _SplashRouter extends ConsumerStatefulWidget {
  const _SplashRouter();

  @override
  ConsumerState<_SplashRouter> createState() => _SplashRouterState();
}

class _SplashRouterState extends ConsumerState<_SplashRouter> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _resolve());
  }

  Future<void> _resolve() async {
    final storage = ref.read(sessionStorageProvider);
    final token = await storage.readToken();
    if (!mounted) return;

    Widget destination = const RegisterScreen();

    if (token != null) {
      try {
        final api = ref.read(identityApiProvider);
        final current = await api.currentSession();
        if (current != null) {
          destination = const HomeScreen();
        } else {
          await storage.clear();
        }
      } catch (_) {
        // Offline / server down / any error — fail forward into register.
      }
    }

    if (!mounted) return;
    await Navigator.of(context).pushReplacement<void, void>(
      MaterialPageRoute<void>(builder: (_) => destination),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: Padding(
            padding: const EdgeInsets.all(AtlasSpace.s800),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  'Atlas',
                  style: AtlasType.displaySection.copyWith(
                    color: AtlasColors.brandPrimary,
                  ),
                ),
                const SizedBox(height: AtlasSpace.s400),
                const CircularProgressIndicator(
                  color: AtlasColors.brandPrimary,
                  strokeWidth: 2,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

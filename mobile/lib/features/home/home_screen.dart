import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../design/components/nav_bar.dart';
import '../../design/tokens/colours.dart';
import '../../design/tokens/spacing.dart';
import '../../design/tokens/typography.dart';
import '../identity/identity_controller.dart';
import '../identity/register_screen.dart';

/// Day 4 placeholder home. Draws + tickets + account tabs land Weeks 5-7.
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
          IconButton(
            icon: const Icon(Icons.logout),
            color: AtlasColors.textPrimary,
            tooltip: 'Sign out',
            onPressed: _signOut,
          ),
        ],
      ),
      body: SafeArea(
        child: Center(
          child: Padding(
            padding: const EdgeInsets.all(AtlasSpace.s800),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  _tabLabel(_tabIndex),
                  style: AtlasType.displaySection.copyWith(
                    color: AtlasColors.brandPrimary,
                  ),
                ),
                const SizedBox(height: AtlasSpace.s400),
                Text(
                  _tabPlaceholder(_tabIndex),
                  textAlign: TextAlign.center,
                  style: AtlasType.bodyDefault.copyWith(
                    color: AtlasColors.textSecondary,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
      bottomNavigationBar: AtlasBottomNav(
        currentIndex: _tabIndex,
        onTap: (i) => setState(() => _tabIndex = i),
        items: const [
          AtlasBottomNavItem(icon: Icons.home_outlined, label: 'HOME'),
          AtlasBottomNavItem(icon: Icons.emoji_events_outlined, label: 'DRAWS'),
          AtlasBottomNavItem(
              icon: Icons.confirmation_number_outlined, label: 'TICKETS'),
          AtlasBottomNavItem(
              icon: Icons.person_outline, label: 'ACCOUNT'),
        ],
      ),
    );
  }

  String _tabLabel(int i) => const ['Home', 'Draws', 'Tickets', 'Account'][i];

  String _tabPlaceholder(int i) => const [
        'Weekly featured draw + latest winner land here in Week 6.',
        'Active + upcoming draws — Week 5.',
        'Your tickets across all draws — Week 5.',
        'Profile, self-exclusion, sign-out — Week 6.',
      ][i];
}

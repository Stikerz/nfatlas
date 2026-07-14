import 'package:flutter/material.dart';

import '../tokens/colours.dart';
import '../tokens/spacing.dart';
import '../tokens/typography.dart';

/// AtlasBottomNav — consumer mobile bottom navigation.
/// Spec: `_bmad-output/planning-artifacts/design/components.md §17.2`.
///
/// 4 slots max per §17.2 (Home, Draws, Tickets, Account in the current V0.5
/// spec). Sidebar variant lives in the admin app under a different name.
class AtlasBottomNavItem {
  const AtlasBottomNavItem({required this.icon, required this.label});
  final IconData icon;
  final String label;
}

class AtlasBottomNav extends StatelessWidget {
  const AtlasBottomNav({
    super.key,
    required this.items,
    required this.currentIndex,
    required this.onTap,
  }) : assert(items.length >= 2 && items.length <= 4);

  final List<AtlasBottomNavItem> items;
  final int currentIndex;
  final ValueChanged<int> onTap;

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: const BoxDecoration(
        color: AtlasColors.surfaceBase,
        border: Border(
          top: BorderSide(color: AtlasColors.dividerHairline),
        ),
      ),
      child: SafeArea(
        top: false,
        child: SizedBox(
          height: 64,
          child: Row(
            children: List.generate(items.length, (i) {
              final selected = i == currentIndex;
              final colour =
                  selected ? AtlasColors.brandPrimary : AtlasColors.textSecondary;
              return Expanded(
                child: Semantics(
                  selected: selected,
                  button: true,
                  label: items[i].label,
                  child: InkWell(
                    onTap: () => onTap(i),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(items[i].icon, size: 24, color: colour),
                        const SizedBox(height: AtlasSpace.s100),
                        Text(
                          items[i].label,
                          style: AtlasType.labelMicro.copyWith(color: colour),
                        ),
                      ],
                    ),
                  ),
                ),
              );
            }),
          ),
        ),
      ),
    );
  }
}

'use client';

import { useRouter } from 'next/navigation';
import { useState } from 'react';

/**
 * AdminTopBar — brand + notification bell + operator identity chip.
 * Spec: `_bmad-output/planning-artifacts/design/wireframes/08-admin-login.md §1.3-1.4`.
 */

interface AdminTopBarProps {
  operatorName: string;
  unreadNotifications?: number;
}

export function AdminTopBar({ operatorName, unreadNotifications = 0 }: AdminTopBarProps) {
  const router = useRouter();
  const [menuOpen, setMenuOpen] = useState(false);

  async function signOut() {
    await fetch('/api/auth/logout', { method: 'POST' });
    router.replace('/login');
  }

  return (
    <header className="sticky top-0 z-[10] flex items-center justify-between border-b border-divider-hairline bg-surface-base px-600 py-300">
      <h1 className="font-display text-[20px] font-semibold leading-[1.2] text-text-primary">
        Atlas Admin
      </h1>
      <div className="flex items-center gap-400">
        <button
          type="button"
          aria-label={`Notifications${unreadNotifications ? `, ${unreadNotifications} unread` : ''}`}
          className="relative inline-flex h-[32px] w-[32px] items-center justify-center rounded-small text-text-secondary hover:bg-surface-subtle focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-focus focus-visible:ring-offset-[2px]"
        >
          <span aria-hidden="true">🔔</span>
          {unreadNotifications > 0 ? (
            <span className="absolute -right-100 -top-100 inline-flex h-[16px] min-w-[16px] items-center justify-center rounded-pill bg-brand-accent px-100 text-[10px] font-medium text-brand-primary">
              {unreadNotifications}
            </span>
          ) : null}
        </button>

        <div className="relative">
          <button
            type="button"
            aria-haspopup="menu"
            aria-expanded={menuOpen}
            onClick={() => setMenuOpen((v) => !v)}
            className="inline-flex items-center gap-200 rounded-small px-300 py-200 text-[16px] leading-[1.6] text-text-primary hover:bg-surface-subtle focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-focus focus-visible:ring-offset-[2px]"
          >
            <span aria-hidden="true">👤</span>
            <span>{operatorName}</span>
            <span aria-hidden="true" className="text-text-secondary">▾</span>
          </button>
          {menuOpen ? (
            <div
              role="menu"
              className="absolute right-0 top-[calc(100%+8px)] w-[200px] rounded-medium border border-divider-hairline bg-surface-base shadow-e1"
            >
              <button
                type="button"
                role="menuitem"
                onClick={signOut}
                className="block w-full px-400 py-300 text-left text-[16px] leading-[1.6] text-text-primary hover:bg-surface-subtle"
              >
                Sign out
              </button>
              <div className="border-t border-divider-hairline" />
              <span
                role="menuitem"
                aria-disabled="true"
                className="block px-400 py-300 text-[16px] leading-[1.6] text-text-secondary"
              >
                Settings (V1)
              </span>
              <span
                role="menuitem"
                aria-disabled="true"
                className="block px-400 py-300 text-[16px] leading-[1.6] text-text-secondary"
              >
                Help
              </span>
            </div>
          ) : null}
        </div>
      </div>
    </header>
  );
}

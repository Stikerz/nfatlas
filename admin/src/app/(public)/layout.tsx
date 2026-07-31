/**
 * Public-facing route group — no auth, no session cookie read.
 *
 * Distinct from (admin) + (auth) so the proof page + trust-story pages
 * ship with no accidental auth dependency. A regulator screenshotting
 * `/proof/{draw_id}` will see identical output to what a public browser
 * sees.
 */

import type { ReactNode } from 'react';

export default function PublicLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-[var(--color-bg-canvas)] text-[var(--color-text-primary)]">
      <header className="border-b border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)]">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <a
            href="/"
            className="font-fraunces text-xl font-bold text-[var(--color-text-primary)] no-underline"
          >
            Atlas
          </a>
          <nav className="flex gap-4 text-sm text-[var(--color-text-secondary)]">
            <a href="/how-it-works" className="hover:text-[var(--color-text-primary)]">
              How it works
            </a>
            <a href="/responsible-play" className="hover:text-[var(--color-text-primary)]">
              Responsible play
            </a>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-5xl px-6 py-10">{children}</main>
      <footer className="border-t border-[var(--color-border-subtle)] py-6 text-center text-sm text-[var(--color-text-secondary)]">
        Atlas · Provably fair prize competitions · Nigeria
      </footer>
    </div>
  );
}

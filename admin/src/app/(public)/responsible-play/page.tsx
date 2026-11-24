/**
 * Trust-story page — responsible play + self-exclusion.
 *
 * Static, no auth, no DB. Copy per v0.5-demo-plan.md §2.16.
 *
 * REVIEW-002 §6 (2026-11-23): this page previously described a permanent
 * self-exclusion regime, an in-app self-exclude flow, and age verification
 * at every purchase. None of the three existed.
 *
 * 2026-11-24: ADR-010 **Phase A** shipped — permanent account closure is
 * now real and enforced (registry row, account closed, all sessions
 * revoked, refused at purchase and at skill-question issue). Copy updated
 * to match, and ONLY to match. Two limits still govern what may be said:
 *   1. No in-app control yet (plan item A5). Today the route is support.
 *   2. No cross-account enforcement. Phase A is account-level; blocking
 *      re-registration needs BVN, which needs ADR-007 (KYC). Do NOT
 *      restore "a fresh account cannot bypass it" until Phase B ships.
 */

import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Responsible play · Atlas',
  description:
    'Atlas takes responsible play seriously. Age is gated at registration and confidential support resources are listed here.',
};

export default function ResponsiblePlayPage() {
  return (
    <article className="prose max-w-none">
      <h1 className="font-fraunces text-3xl font-bold md:text-4xl">
        Responsible play
      </h1>
      <p className="mt-4 text-lg text-[var(--color-text-secondary)]">
        Atlas is a prize competition. It should be fun and time-boxed.
      </p>

      <section className="mt-10">
        <h2 className="mb-3 text-xl font-semibold">Our commitments</h2>
        <ul className="list-disc space-y-2 pl-6">
          <li>
            You must be <strong>18 or older</strong>. Date of birth is
            checked when you register, and an account that fails that check
            is never created.
          </li>
          <li>
            <strong>You can close your account permanently.</strong> Ask us
            and we will close it for good — the decision is recorded, every
            active session is ended, and the account can no longer enter any
            draw. There is no undo, by design.
          </li>
          <li>
            We never send you notifications encouraging you to enter more
            draws. Draw close reminders can be turned off.
          </li>
        </ul>
      </section>

      <section className="mt-8">
        <h2 className="mb-3 text-xl font-semibold">
          Closing your account permanently
        </h2>
        <p>
          Email{' '}
          <a href="mailto:support@atlas.example" className="underline">
            support@atlas.example
          </a>{' '}
          from the address on your account and ask us to close it. Once we
          do, the account is closed for good: you are signed out everywhere
          and no further entry is possible, on any route. We cannot reopen
          it, and we will not ask you to confirm twice or try to talk you
          out of it.
        </p>
        <p className="mt-3">
          You can also do it yourself in the app:{' '}
          <em>Account → Close my account</em>. You will be asked to type
          EXCLUDE and confirm with a code we send you. Email works just as
          well if you would rather not do it alone.
        </p>
        <p className="mt-3">
          <strong>If you have money in your account,</strong> closing it does
          not forfeit the balance. We hold it and support will arrange
          payment to you — it will not simply disappear, and you do not need
          to withdraw it first.
        </p>
        <p className="mt-3">
          One further limit, stated plainly: closing your account stops{' '}
          <em>that account</em>. It does not currently stop someone opening
          a new one with a different email and phone number. Making that
          impossible requires identity verification we have not built yet.
          If stopping matters to you, the support resources below are worth
          more than our account controls.
        </p>
      </section>

      <section className="mt-8">
        <h2 className="mb-3 text-xl font-semibold">Support resources</h2>
        <p>
          If Atlas has stopped being fun, or you find yourself entering more
          than you intended, these organisations offer confidential
          support:
        </p>
        <ul className="list-disc space-y-2 pl-6">
          <li>
            <strong>GamCare (UK)</strong> — support for gambling-related
            harm. UK-based; listed because its resources are freely
            accessible online.{' '}
            <a href="https://www.gamcare.org.uk" target="_blank" rel="noopener noreferrer" className="underline">
              gamcare.org.uk
            </a>
          </li>
          <li>
            <strong>Federation of Muslim Women&apos;s Associations in Nigeria</strong>
            {' '}— confidential counselling.
          </li>
          <li>
            <strong>Mentally Aware Nigeria Initiative (MANI)</strong> —{' '}
            <a href="https://mentallyaware.org" target="_blank" rel="noopener noreferrer" className="underline">
              mentallyaware.org
            </a>
          </li>
        </ul>
      </section>

      <section className="mt-8 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-canvas)] p-5">
        <h2 className="mb-2 text-lg font-semibold">Age is a hard gate</h2>
        <p className="text-sm">
          Registration is refused if your date of birth puts you under 18.
          This is a legal requirement and a personal one.
        </p>
      </section>
    </article>
  );
}

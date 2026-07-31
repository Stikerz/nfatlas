/**
 * Trust-story page — responsible play + self-exclusion.
 *
 * Static, no auth, no DB. Copy per v0.5-demo-plan.md §2.16 with the
 * founder-approved framing: prize competition, not gambling; but the
 * self-exclusion + support-service posture is real and permanent.
 */

import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Responsible play · Atlas',
  description:
    'Atlas takes responsible play seriously. Self-exclusion is a permanent commitment; support resources are one tap away.',
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
            You must be <strong>18 or older</strong> to enter. Age is
            verified at registration and at every purchase.
          </li>
          <li>
            <strong>Self-exclusion is permanent.</strong> If you choose to
            self-exclude, we retain that decision indefinitely — a fresh
            account with the same phone or bank details cannot bypass it.
          </li>
          <li>
            We never send you notifications encouraging you to enter more
            draws. Draw close reminders can be turned off.
          </li>
          <li>
            <strong>Free entry route always available.</strong> The paid
            route is not the only way to enter — the free route works and is
            not disadvantaged in the odds.
          </li>
        </ul>
      </section>

      <section className="mt-8">
        <h2 className="mb-3 text-xl font-semibold">Self-exclude now</h2>
        <p>
          In-app: <em>Settings → Account → Self-exclude</em>. Confirmation
          requires re-entering your phone number. Once confirmed, the
          account is closed and cannot be reopened.
        </p>
        <p className="mt-3">
          If you cannot access the app, email{' '}
          <a href="mailto:support@atlas.example" className="underline">
            support@atlas.example
          </a>{' '}
          from the phone number on your account. We will action the
          request within one working day.
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
            <strong>GamCare Nigeria</strong> — mental-health support for
            problem gambling.{' '}
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
          If you cannot verify you are 18 or older, the platform will not
          accept an entry from you — paid or free. This is a legal
          requirement and a personal one.
        </p>
      </section>
    </article>
  );
}

/**
 * Trust-story page — how an Atlas draw works.
 *
 * Static, no auth, no DB. Copy per v0.5-demo-plan.md §2.15.
 *
 * 2026-11-26 (AMEND-003): the skill question was removed, as the free
 * entry route was on 2026-11-23. Atlas no longer relies on any mechanic
 * to sit outside gambling regulation — lawfulness rests on holding a
 * State gaming licence, which is being pursued and is NOT yet held.
 *
 * Per REVIEW-001 §2.1, Atlas must not assert its own regulatory
 * classification in consumer copy. With no mechanic left to support the
 * "prize competition" claim, this page now describes the MECHANIC and
 * lets the licence speak to the classification. The copy bans on
 * "lottery", "raffle" and "luck" remain in force and unchanged.
 */

import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'How Atlas works · Provably fair draws',
  description:
    'Every Atlas draw publishes a cryptographic commitment before entries open, and the winner can be verified by anyone after the reveal.',
};

export default function HowItWorksPage() {
  return (
    <article className="prose max-w-none">
      <h1 className="font-fraunces text-3xl font-bold md:text-4xl">
        How Atlas works
      </h1>
      <p className="mt-4 text-lg text-[var(--color-text-secondary)]">
        Every draw is provably fair — and you can check it yourself.
      </p>

      <section className="mt-10">
        <h2 className="mb-3 text-xl font-semibold">What Atlas is</h2>
        <p>
          Each Atlas draw has a prize (cash, an apartment, a car), a fixed
          entry price, and a fixed close time. You buy an entry; each entry
          is one ticket in the draw and carries the same odds as every
          other. You can enter as many times as you like.
        </p>
      </section>

      <section className="mt-8">
        <h2 className="mb-3 text-xl font-semibold">
          Provably fair — verify the winner yourself
        </h2>
        <p>
          When a draw is created, we generate a random <em>server seed</em>
          and publish its SHA-256 <em>commitment</em>. The seed itself stays
          sealed until the draw is revealed. This is a
          <strong> commit-reveal </strong>
          protocol: it proves the operator could not have known the winner
          in advance.
        </p>
        <p className="mt-3">
          At reveal, we fetch a Bitcoin block hash and a drand random-beacon
          round (two independent sources of public randomness), publish
          them alongside the server seed, and run a deterministic algorithm
          to pick the winner + reserves. Every input is published; the
          verifier script re-runs the algorithm and reaches the same
          winner.
        </p>
        <p className="mt-3">
          <a href="/proof" className="underline">
            Browse the proof of a recent draw
          </a>
          , or download{' '}
          <a
            href="https://github.com/Stikerz/nfatlas/blob/main/backend/tools/verify_draw.py"
            target="_blank"
            rel="noopener noreferrer"
            className="underline"
          >
            the verifier script
          </a>{' '}
          and run it yourself.
        </p>
      </section>

      <section className="mt-8">
        <h2 className="mb-3 text-xl font-semibold">Age + entry limits</h2>
        <p>
          You must be 18 or older to enter. We enforce this at registration
          and again at every ticket purchase. If you want to stop, you can
          self-exclude — see{' '}
          <a href="/responsible-play" className="underline">
            responsible play
          </a>
          .
        </p>
      </section>
    </article>
  );
}

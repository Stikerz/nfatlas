/**
 * Trust-story page — how Atlas works as a prize competition.
 *
 * Static, no auth, no DB. Copy per v0.5-demo-plan.md §2.15. Language
 * follows the prize-competition + free-entry-route framing per Adaeze
 * §5 guidance — the word "lottery" appears nowhere.
 */

import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'How Atlas works · Provably fair prize competitions',
  description:
    'Atlas runs prize competitions with a free entry route and a skill question. The winner is chosen by a commit-reveal protocol you can verify yourself.',
};

export default function HowItWorksPage() {
  return (
    <article className="prose max-w-none">
      <h1 className="font-fraunces text-3xl font-bold md:text-4xl">
        How Atlas works
      </h1>
      <p className="mt-4 text-lg text-[var(--color-text-secondary)]">
        A prize competition, not a lottery. Every draw is provably fair.
      </p>

      <section className="mt-10">
        <h2 className="mb-3 text-xl font-semibold">What Atlas is</h2>
        <p>
          Atlas runs <strong>prize competitions</strong>. Each competition has
          a prize (cash, an apartment, a car), a ticket price, and a fixed
          close time. To enter, you either buy a ticket after answering a
          <strong> skill question</strong>, or send us a signed slip through
          the <strong>free entry route</strong>. Both routes go into the same
          ticket pool with the same odds per entry.
        </p>
      </section>

      <section className="mt-8">
        <h2 className="mb-3 text-xl font-semibold">The skill question</h2>
        <p>
          Before you can buy a paid ticket, you answer one multiple-choice
          question rotated from a curated pool. A wrong answer serves you a
          new question — no penalty, no lockout. The skill test is the legal
          basis for the competition status, and we take it seriously: the
          pool grows over time and rotates deterministically per user per
          minute so nobody can farm easy questions.
        </p>
      </section>

      <section className="mt-8">
        <h2 className="mb-3 text-xl font-semibold">The free entry route</h2>
        <p>
          Under Nigerian and UK prize-competition norms, a free way to enter
          must exist. Ours: mail a written entry slip to the address on the
          draw page. Our operator transcribes the slip and it enters the
          same ticket pool, with the same odds per entry, as any paid ticket.
          Free entries are indistinguishable from paid ones by the winner-
          selection algorithm.
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

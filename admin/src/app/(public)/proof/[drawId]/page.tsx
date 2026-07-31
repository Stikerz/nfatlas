/**
 * Public draw-proof page — the trust surface (SSR).
 *
 * Route: /proof/[drawId]
 * Auth:  none — public per ADR-006 §Protocol stage 4.
 *
 * Fetches GET /api/v1/draws/{id}/proof on the server. Renders:
 *   - Header with prize + state badge.
 *   - Commitment (monospace, verbatim).
 *   - Post-reveal grid: server_seed, tickets_hash, bitcoin block
 *     (with height link to mempool.space), drand round + randomness.
 *   - Winners table (position, is_primary, ticket_id short,
 *     user_id_hash short).
 *   - Verify block: copy-command with the exact `verify_draw.py`
 *     invocation for the current draw + host.
 *   - Link to ADR-006 (GitHub) as algorithm reference.
 *
 * Zero JS on first paint — only the CopyCommand island hydrates.
 * A regulator screenshotting the printed page sees the full proof.
 */

import { notFound } from 'next/navigation';

import { atlasFetch } from '@/lib/api-client';
import { shortHex, verifyCommandFor } from '@/lib/proof-format';

import CopyCommand from './CopyCommand';

interface DrawProof {
  id: string;
  state: 'draft' | 'committed' | 'sales_open' | 'sales_closed' | 'revealed';
  commitment: string;
  close_time: string;
  draw_time: string;
  revealed_at?: string | null;
  server_seed?: string | null;
  tickets_hash?: string | null;
  ticket_count?: number | null;
  ordered_ticket_ids?: string[] | null;
  entropy?: {
    mode: string;
    bitcoin_hash: string;
    bitcoin_height: number;
    bitcoin_timestamp: number;
    drand_round: number;
    drand_randomness: string;
    drand_signature: string;
    verified_at: string;
  } | null;
  winners?: {
    position: number;
    is_primary: boolean;
    ticket_id: string;
    user_id_hash: string;
  }[] | null;
  algorithm_reference?: string | null;
  reserves?: number | null;
}

interface PageProps {
  params: { drawId: string };
}

const PUBLIC_API_BASE =
  process.env.ATLAS_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

function StateBadge({ state }: { state: DrawProof['state'] }) {
  const styles: Record<DrawProof['state'], string> = {
    draft: 'bg-[var(--color-bg-canvas)] text-[var(--color-text-secondary)]',
    committed: 'bg-[var(--color-accent-warm-bg)] text-[var(--color-accent-warm)]',
    sales_open: 'bg-[var(--color-accent-success-bg)] text-[var(--color-accent-success)]',
    sales_closed: 'bg-[var(--color-accent-warm-bg)] text-[var(--color-accent-warm)]',
    revealed: 'bg-[var(--color-accent-primary-bg)] text-[var(--color-accent-primary)]',
  };
  return (
    <span
      className={`inline-block rounded-full px-3 py-1 text-xs font-medium uppercase tracking-wide ${styles[state] ?? styles.draft}`}
    >
      {state.replace('_', ' ')}
    </span>
  );
}

function KeyRow({ label, value, mono = false }: { label: string; value: React.ReactNode; mono?: boolean }) {
  return (
    <div className="flex flex-col gap-1 border-b border-[var(--color-border-subtle)] py-3 last:border-b-0 md:flex-row md:gap-6">
      <dt className="w-full text-sm text-[var(--color-text-secondary)] md:w-56 md:shrink-0">{label}</dt>
      <dd
        className={
          mono
            ? 'flex-1 break-all font-mono text-sm text-[var(--color-text-primary)]'
            : 'flex-1 text-sm text-[var(--color-text-primary)]'
        }
      >
        {value}
      </dd>
    </div>
  );
}

export default async function ProofPage({ params }: PageProps) {
  const { drawId } = params;

  const response = await atlasFetch<DrawProof>(`/api/v1/draws/${drawId}/proof`);
  if (!response.ok || !response.body) {
    if (response.status === 404) notFound();
    throw new Error(response.errorMessage ?? 'proof fetch failed');
  }
  const proof = response.body;
  const isRevealed = proof.state === 'revealed';

  const verifyCommand = verifyCommandFor(proof.id, PUBLIC_API_BASE);

  return (
    <article>
      <div className="mb-8 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-xs uppercase tracking-wide text-[var(--color-text-secondary)]">
            Draw proof
          </p>
          <h1 className="mt-1 font-fraunces text-2xl font-bold md:text-3xl">
            {proof.id}
          </h1>
        </div>
        <StateBadge state={proof.state} />
      </div>

      <section className="mb-8 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)] p-5">
        <h2 className="mb-2 text-lg font-semibold">Commitment</h2>
        <p className="mb-3 text-sm text-[var(--color-text-secondary)]">
          Published at draw creation. The operator cannot have known any winner
          before revealing the seed below.
        </p>
        <dl>
          <KeyRow label="Commitment (SHA-256)" value={proof.commitment} mono />
          <KeyRow label="Close time" value={proof.close_time} />
          <KeyRow label="Draw time" value={proof.draw_time} />
        </dl>
      </section>

      {isRevealed && proof.entropy && proof.winners ? (
        <>
          <section className="mb-8 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)] p-5">
            <h2 className="mb-2 text-lg font-semibold">Revealed inputs</h2>
            <p className="mb-3 text-sm text-[var(--color-text-secondary)]">
              Every input the winner-selection algorithm consumed. Fetched
              once, published verbatim, hashed into the audit chain.
            </p>
            <dl>
              <KeyRow label="Revealed at" value={proof.revealed_at ?? ''} />
              <KeyRow label="Server seed (SHA-256)" value={proof.server_seed ?? ''} mono />
              <KeyRow label="Tickets hash" value={proof.tickets_hash ?? ''} mono />
              <KeyRow label="Ticket count" value={String(proof.ticket_count ?? 0)} />
              <KeyRow label="Bitcoin block hash" value={proof.entropy.bitcoin_hash} mono />
              <KeyRow
                label="Bitcoin block height"
                value={
                  <a
                    href={`https://mempool.space/block/${proof.entropy.bitcoin_hash}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="underline"
                  >
                    #{proof.entropy.bitcoin_height} on mempool.space
                  </a>
                }
              />
              <KeyRow
                label="drand round"
                value={
                  <a
                    href={`https://api.drand.sh/public/${proof.entropy.drand_round}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="underline"
                  >
                    #{proof.entropy.drand_round} on drand
                  </a>
                }
              />
              <KeyRow label="drand randomness" value={proof.entropy.drand_randomness} mono />
              <KeyRow label="Entropy mode" value={proof.entropy.mode} />
            </dl>
          </section>

          <section className="mb-8 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)] p-5">
            <h2 className="mb-3 text-lg font-semibold">
              Winner + {proof.reserves ?? 0} reserves
            </h2>
            <table className="w-full text-left text-sm">
              <thead className="border-b border-[var(--color-border-subtle)] text-[var(--color-text-secondary)]">
                <tr>
                  <th className="py-2 pr-4">Position</th>
                  <th className="py-2 pr-4">Ticket</th>
                  <th className="py-2 pr-4">Winner id (hash)</th>
                </tr>
              </thead>
              <tbody className="font-mono">
                {proof.winners.map((w) => (
                  <tr key={w.ticket_id} className="border-b border-[var(--color-border-subtle)] last:border-b-0">
                    <td className="py-2 pr-4">
                      {w.is_primary ? (
                        <strong className="text-[var(--color-accent-primary)]">Primary</strong>
                      ) : (
                        `Reserve #${w.position}`
                      )}
                    </td>
                    <td className="py-2 pr-4">{shortHex(w.ticket_id)}</td>
                    <td className="py-2 pr-4">{shortHex(w.user_id_hash)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>

          <section className="mb-8 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)] p-5">
            <h2 className="mb-2 text-lg font-semibold">Verify this yourself</h2>
            <p className="mb-2 text-sm text-[var(--color-text-secondary)]">
              Run the CLI below. Same server seed, same entropy, same tickets
              hash — you should compute the same winner ticket id we published.
            </p>
            <CopyCommand command={verifyCommand} />
            {proof.algorithm_reference ? (
              <p className="mt-3 text-sm">
                Algorithm reference:{' '}
                <a
                  href={proof.algorithm_reference}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="underline"
                >
                  ADR-006 — Commit-reveal protocol
                </a>
              </p>
            ) : null}
          </section>
        </>
      ) : (
        <section className="mb-8 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)] p-5">
          <h2 className="mb-2 text-lg font-semibold">Reveal pending</h2>
          <p className="text-sm text-[var(--color-text-secondary)]">
            The server seed remains sealed until the draw is revealed. Come
            back after <strong>{proof.draw_time}</strong> to see the full
            proof + winner.
          </p>
        </section>
      )}
    </article>
  );
}

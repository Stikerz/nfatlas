/**
 * Admin — draws list + create form.
 *
 * Server component reads GET /api/v1/draws server-side (bearer from
 * cookie via the layout's session). The inline NewDrawForm client
 * component POSTs through the /api/admin/draws proxy.
 */

import { cookies } from 'next/headers';
import Link from 'next/link';

import { atlasFetch } from '@/lib/api-client';
import { readAdminToken } from '@/lib/session';

import NewDrawForm from './NewDrawForm';

interface DrawSummary {
  id: string;
  prize_copy: string;
  ticket_price_minor: number;
  currency: string;
  close_time: string;
  draw_time: string;
  state: string;
  commitment: string;
}

interface DrawListResponse {
  items: DrawSummary[];
}

function StateBadge({ state }: { state: string }) {
  const styles: Record<string, string> = {
    draft: 'bg-divider-hairline text-text-secondary',
    committed: 'bg-state-attention/20 text-state-attention',
    sales_open: 'bg-state-success/20 text-state-success',
    sales_closed: 'bg-state-attention/20 text-state-attention',
    revealed: 'bg-brand-primary/20 text-brand-primary',
  };
  return (
    <span
      className={`inline-block rounded-full px-300 py-100 text-[11px] font-medium uppercase tracking-wide ${styles[state] ?? styles.draft}`}
    >
      {state.replace('_', ' ')}
    </span>
  );
}

export default async function AdminDrawsPage() {
  const token = readAdminToken(await cookies());
  const response = await atlasFetch<DrawListResponse>('/api/v1/draws', {
    bearerToken: token,
  });
  const draws = response.body?.items ?? [];

  return (
    <div className="flex flex-col gap-800">
      <div>
        <p className="text-[12px] font-medium uppercase tracking-[0.05em] text-brand-accent">
          ▪ Operate
        </p>
        <h2 className="mt-200 font-display text-[32px] font-semibold text-text-primary">
          Draws
        </h2>
        <p className="mt-200 text-[15px] text-text-secondary">
          Create + close + reveal draws. Public trust surface is{' '}
          <Link href="/proof" className="underline">
            /proof/[drawId]
          </Link>
          .
        </p>
      </div>

      <NewDrawForm />

      <section>
        <h3 className="mb-400 font-display text-[20px] font-semibold text-text-primary">
          Active draws
        </h3>
        {draws.length === 0 ? (
          <p className="rounded-large border border-divider-hairline bg-surface-elevated p-600 text-[14px] text-text-secondary">
            No active draws. Create one above.
          </p>
        ) : (
          <ul className="flex flex-col gap-300">
            {draws.map((draw) => (
              <li
                key={draw.id}
                className="rounded-large border border-divider-hairline bg-surface-elevated p-500"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-display text-[18px] font-semibold text-text-primary">
                      {draw.prize_copy}
                    </p>
                    <p className="mt-200 text-[13px] text-text-secondary">
                      Closes {new Date(draw.close_time).toLocaleString()} · ₦
                      {(draw.ticket_price_minor / 100).toFixed(2)}
                    </p>
                    <p className="mt-100 font-mono text-[11px] text-text-secondary">
                      {draw.commitment.slice(0, 16)}…{draw.commitment.slice(-16)}
                    </p>
                  </div>
                  <div className="flex flex-col items-end gap-300">
                    <StateBadge state={draw.state} />
                    <Link
                      href={`/admin/draws/${draw.id}`}
                      className="rounded bg-brand-primary px-400 py-200 text-[13px] font-medium text-text-inverted"
                    >
                      Open
                    </Link>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

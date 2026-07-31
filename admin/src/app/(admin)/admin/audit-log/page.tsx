/**
 * Admin — audit log table.
 *
 * Server component reads GET /api/v1/audit-log with the operator's
 * bearer from cookies. Filters + pagination are query-string driven
 * so the URL is shareable + copy-pasteable for incident work.
 */

import { cookies } from 'next/headers';

import { atlasFetch } from '@/lib/api-client';
import { readAdminToken } from '@/lib/session';

interface AuditEntry {
  seq: number;
  occurred_at: string;
  actor_type: string;
  actor_id: string | null;
  event_name: string;
  subject_type: string;
  subject_id: string;
  payload: Record<string, unknown>;
  prev_hash: string;
  row_hash: string;
}

interface AuditPage {
  items: AuditEntry[];
  next_before_seq: number | null;
  chain_verified: boolean;
  chain_verify_reason: string | null;
}

interface PageProps {
  searchParams: Promise<{
    event_name?: string;
    subject_type?: string;
    before_seq?: string;
    limit?: string;
  }>;
}

function short(hex: string, chars = 8): string {
  if (hex.length <= chars * 2 + 1) return hex;
  return `${hex.slice(0, chars)}…${hex.slice(-chars)}`;
}

export default async function AdminAuditLogPage({ searchParams }: PageProps) {
  const sp = await searchParams;
  const token = readAdminToken(await cookies());

  const params = new URLSearchParams();
  if (sp.event_name) params.set('event_name', sp.event_name);
  if (sp.subject_type) params.set('subject_type', sp.subject_type);
  params.set('limit', sp.limit ?? '50');
  if (sp.before_seq) params.set('before_seq', sp.before_seq);

  const response = await atlasFetch<AuditPage>(
    `/api/v1/audit-log?${params.toString()}`,
    { bearerToken: token },
  );
  const page: AuditPage = response.body ?? {
    items: [],
    next_before_seq: null,
    chain_verified: true,
    chain_verify_reason: null,
  };

  const nextUrl = page.next_before_seq
    ? `/admin/audit-log?${new URLSearchParams({
        ...(sp.event_name ? { event_name: sp.event_name } : {}),
        ...(sp.subject_type ? { subject_type: sp.subject_type } : {}),
        limit: sp.limit ?? '50',
        before_seq: String(page.next_before_seq),
      }).toString()}`
    : null;

  return (
    <div className="flex flex-col gap-600">
      <div>
        <p className="text-[12px] font-medium uppercase tracking-[0.05em] text-brand-accent">
          ▪ Trust
        </p>
        <h2 className="mt-200 font-display text-[32px] font-semibold text-text-primary">
          Audit log
        </h2>
        <p className="mt-200 text-[15px] text-text-secondary">
          Hash-chained event stream. Every state change lands here per
          ADR-005.
        </p>
      </div>

      <form className="flex flex-wrap items-end gap-300 rounded-large border border-divider-hairline bg-surface-elevated p-400">
        <label className="flex flex-col text-[12px] text-text-secondary">
          Event name
          <input
            type="text"
            name="event_name"
            defaultValue={sp.event_name ?? ''}
            placeholder="draw.revealed"
            className="mt-100 rounded border border-divider-strong bg-surface-base px-300 py-200 text-[13px] text-text-primary"
          />
        </label>
        <label className="flex flex-col text-[12px] text-text-secondary">
          Subject type
          <input
            type="text"
            name="subject_type"
            defaultValue={sp.subject_type ?? ''}
            placeholder="draw"
            className="mt-100 rounded border border-divider-strong bg-surface-base px-300 py-200 text-[13px] text-text-primary"
          />
        </label>
        <label className="flex flex-col text-[12px] text-text-secondary">
          Limit
          <input
            type="number"
            name="limit"
            defaultValue={sp.limit ?? '50'}
            min="1"
            max="500"
            className="mt-100 w-[120px] rounded border border-divider-strong bg-surface-base px-300 py-200 text-[13px] text-text-primary"
          />
        </label>
        <button
          type="submit"
          className="rounded bg-brand-primary px-400 py-200 text-[13px] font-medium text-text-inverted"
        >
          Filter
        </button>
      </form>

      <div
        className={`rounded p-300 text-[13px] font-medium ${
          page.chain_verified
            ? 'bg-state-success/15 text-state-success'
            : 'bg-state-danger/15 text-state-danger'
        }`}
      >
        {page.chain_verified
          ? '✓ Chain verified across this page'
          : `✗ Chain break: ${page.chain_verify_reason ?? 'unknown'}`}
      </div>

      <div className="overflow-x-auto rounded-large border border-divider-hairline">
        <table className="w-full text-left text-[13px]">
          <thead className="bg-surface-elevated text-text-secondary">
            <tr>
              <th className="py-300 pl-400">Seq</th>
              <th className="py-300">Time</th>
              <th className="py-300">Event</th>
              <th className="py-300">Actor</th>
              <th className="py-300">Subject</th>
              <th className="py-300 pr-400">Row hash</th>
            </tr>
          </thead>
          <tbody>
            {page.items.map((entry) => (
              <tr
                key={entry.seq}
                className="border-t border-divider-hairline"
              >
                <td className="py-300 pl-400 font-mono">{entry.seq}</td>
                <td className="py-300 font-mono text-[12px]">
                  {new Date(entry.occurred_at).toLocaleString()}
                </td>
                <td className="py-300">{entry.event_name}</td>
                <td className="py-300 text-text-secondary">
                  {entry.actor_type}
                  {entry.actor_id ? ` · ${short(entry.actor_id)}` : ''}
                </td>
                <td className="py-300 text-text-secondary">
                  {entry.subject_type} · {short(entry.subject_id)}
                </td>
                <td className="py-300 pr-400 font-mono text-[11px]">
                  {short(entry.row_hash)}
                </td>
              </tr>
            ))}
            {page.items.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-500 text-center text-text-secondary">
                  No matching audit events.
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>

      {nextUrl ? (
        <div>
          <a
            href={nextUrl}
            className="text-[13px] text-brand-primary underline"
          >
            Older →
          </a>
        </div>
      ) : null}
    </div>
  );
}

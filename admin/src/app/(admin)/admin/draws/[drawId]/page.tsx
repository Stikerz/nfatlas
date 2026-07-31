import { cookies } from 'next/headers';
import Link from 'next/link';
import { notFound } from 'next/navigation';

import { atlasFetch } from '@/lib/api-client';
import { readAdminToken } from '@/lib/session';

import ActionButton from './ActionButtons';

interface DrawDetail {
  id: string;
  prize_copy: string;
  ticket_price_minor: number;
  currency: string;
  close_time: string;
  draw_time: string;
  state: string;
  commitment: string;
}

interface WinnerRow {
  position: number;
  is_primary: boolean;
  ticket_id: string;
  user_id: string;
  contact_status: string;
}

interface WinnerListResponse {
  items: WinnerRow[];
}

interface PageProps {
  params: Promise<{ drawId: string }>;
}

export default async function AdminDrawDetailPage({ params }: PageProps) {
  const { drawId } = await params;
  const token = readAdminToken(await cookies());
  const drawResp = await atlasFetch<DrawDetail>(`/api/v1/draws/${drawId}`, {
    bearerToken: token,
  });
  if (drawResp.status === 404) notFound();
  if (!drawResp.ok || !drawResp.body) {
    throw new Error(drawResp.errorMessage ?? 'draw fetch failed');
  }
  const draw = drawResp.body;

  const winnersResp = await atlasFetch<WinnerListResponse>(
    `/api/v1/draws/${drawId}/winners`,
    { bearerToken: token },
  );
  const winners = winnersResp.body?.items ?? [];

  return (
    <div className="flex flex-col gap-800">
      <div>
        <Link
          href="/admin/draws"
          className="text-[13px] text-text-secondary underline"
        >
          ← All draws
        </Link>
        <h2 className="mt-200 font-display text-[32px] font-semibold text-text-primary">
          {draw.prize_copy}
        </h2>
        <p className="mt-200 text-[14px] text-text-secondary">
          State: <strong>{draw.state}</strong> · ₦
          {(draw.ticket_price_minor / 100).toFixed(2)} · Closes{' '}
          {new Date(draw.close_time).toLocaleString()}
        </p>
        <p className="mt-200 font-mono text-[12px] text-text-secondary">
          commitment {draw.commitment}
        </p>
      </div>

      <section>
        <h3 className="mb-400 font-display text-[18px] font-semibold">
          Lifecycle actions
        </h3>
        <div className="flex flex-col gap-400">
          {draw.state === 'sales_open' ? (
            <ActionButton drawId={draw.id} action="close" label="Close draw" />
          ) : null}
          {draw.state === 'sales_closed' ? (
            <ActionButton
              drawId={draw.id}
              action="reveal"
              label="Reveal winner"
            />
          ) : null}
          {draw.state === 'revealed' ? (
            <Link
              href={`/proof/${draw.id}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-[14px] text-brand-primary underline"
            >
              View public proof →
            </Link>
          ) : null}
        </div>
      </section>

      {winners.length > 0 ? (
        <section>
          <h3 className="mb-400 font-display text-[18px] font-semibold">
            Winners
          </h3>
          <table className="w-full text-left text-[13px]">
            <thead className="border-b border-divider-hairline text-text-secondary">
              <tr>
                <th className="py-200 pr-400">Position</th>
                <th className="py-200 pr-400">Ticket</th>
                <th className="py-200 pr-400">Contact status</th>
              </tr>
            </thead>
            <tbody className="font-mono">
              {winners.map((w) => (
                <tr
                  key={w.ticket_id}
                  className="border-b border-divider-hairline last:border-b-0"
                >
                  <td className="py-300 pr-400">
                    {w.is_primary ? (
                      <strong className="text-brand-primary">Primary</strong>
                    ) : (
                      `Reserve #${w.position}`
                    )}
                  </td>
                  <td className="py-300 pr-400">
                    {w.ticket_id.slice(0, 12)}…{w.ticket_id.slice(-12)}
                  </td>
                  <td className="py-300 pr-400">{w.contact_status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      ) : null}
    </div>
  );
}

/**
 * Admin — self-exclusion registry (read-only).
 *
 * ADR-010 Phase A, build-plan item A6. Server component reads
 * GET /api/v1/self-exclusions with the operator's bearer from cookies.
 *
 * READ-ONLY BY DESIGN. There is deliberately no un-exclude control here,
 * and there must never be one in V1: exclusion is permanent and the
 * absence of the affordance is part of the enforcement (ADR-010 amendment
 * §Invariants added). If an operator needs to discuss a case, they do it
 * with the user, not with this table.
 */

import { cookies } from 'next/headers';

import { atlasFetch } from '@/lib/api-client';
import { readAdminToken } from '@/lib/session';

interface SelfExclusion {
  user_id: string;
  email: string;
  excluded_at: string;
  excluded_by: string;
  excluded_by_id: string | null;
  reason: string | null;
  bvn_enforced: boolean;
}

interface SelfExclusionList {
  items: SelfExclusion[];
}

export default async function AdminSelfExclusionsPage() {
  const token = readAdminToken(await cookies());
  const response = await atlasFetch<SelfExclusionList>('/api/v1/self-exclusions', {
    bearerToken: token,
  });
  const items = response.body?.items ?? [];

  return (
    <div className="flex flex-col gap-600">
      <div>
        <p className="text-[12px] font-medium uppercase tracking-[0.05em] text-brand-accent">
          ▪ Review
        </p>
        <h2 className="mt-200 font-display text-[32px] font-semibold text-text-primary">
          Self-exclusions
        </h2>
        <p className="mt-200 text-[15px] text-text-secondary">
          Permanent account closures under ADR-010. This list is read-only —
          V1 has no reversal, and there is no operator control that can undo
          an entry.
        </p>
      </div>

      <div className="rounded-large border border-divider-hairline bg-surface-elevated p-400">
        <p className="text-[13px] text-text-secondary">
          <strong className="text-text-primary">Phase A.</strong> Enforcement
          is account-level: a closed account cannot log in or enter any draw.
          It does <strong className="text-text-primary">not</strong> prevent
          the same person registering again with a different email and phone —
          that requires BVN matching, which depends on ADR-007 (KYC) and is not
          built. Rows showing <em>BVN enforced: no</em> carry that limitation.
        </p>
      </div>

      {items.length === 0 ? (
        <p className="text-[15px] text-text-secondary">
          No self-exclusions recorded.
        </p>
      ) : (
        <div className="overflow-x-auto rounded-large border border-divider-hairline">
          <table className="w-full border-collapse text-[13px]">
            <thead>
              <tr className="bg-surface-elevated text-left text-text-secondary">
                <th className="px-300 py-200 font-medium">Excluded at</th>
                <th className="px-300 py-200 font-medium">Account</th>
                <th className="px-300 py-200 font-medium">By</th>
                <th className="px-300 py-200 font-medium">Reason</th>
                <th className="px-300 py-200 font-medium">BVN enforced</th>
              </tr>
            </thead>
            <tbody>
              {items.map((row) => (
                <tr
                  key={row.user_id}
                  className="border-t border-divider-hairline text-text-primary"
                >
                  <td className="px-300 py-200 tabular-nums">
                    {new Date(row.excluded_at).toISOString().replace('T', ' ').slice(0, 19)}
                  </td>
                  <td className="px-300 py-200">{row.email}</td>
                  <td className="px-300 py-200">{row.excluded_by}</td>
                  <td className="px-300 py-200 text-text-secondary">
                    {row.reason ?? '—'}
                  </td>
                  <td className="px-300 py-200">
                    {row.bvn_enforced ? 'yes' : 'no'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

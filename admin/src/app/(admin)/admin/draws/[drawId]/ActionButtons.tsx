'use client';

import { useRouter } from 'next/navigation';
import { useState } from 'react';

interface Props {
  drawId: string;
  action: 'close' | 'reveal';
  label: string;
}

/**
 * Two-step admin action: click → confirm → POST. On success, refresh
 * the server component so the state badge + winners table update.
 */
export default function ActionButton({ drawId, action, label }: Props) {
  const router = useRouter();
  const [confirming, setConfirming] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit() {
    setSubmitting(true);
    setError(null);
    const response = await fetch(`/api/admin/draws/${drawId}/${action}`, {
      method: 'POST',
    });
    setSubmitting(false);
    setConfirming(false);
    if (!response.ok) {
      const body = (await response.json().catch(() => ({}))) as {
        message?: string;
        error?: string;
      };
      setError(body.message ?? body.error ?? 'Action failed.');
      return;
    }
    router.refresh();
  }

  return (
    <div>
      {confirming ? (
        <div className="flex items-center gap-300">
          <span className="text-[13px] text-text-secondary">
            Confirm — this is not reversible.
          </span>
          <button
            type="button"
            onClick={submit}
            disabled={submitting}
            className="rounded bg-state-danger px-400 py-200 text-[13px] font-medium text-text-inverted disabled:opacity-60"
          >
            {submitting ? 'Working…' : `Yes, ${label.toLowerCase()}`}
          </button>
          <button
            type="button"
            onClick={() => setConfirming(false)}
            disabled={submitting}
            className="text-[13px] text-text-secondary underline disabled:opacity-60"
          >
            Cancel
          </button>
        </div>
      ) : (
        <button
          type="button"
          onClick={() => setConfirming(true)}
          className="rounded border border-brand-primary bg-surface-base px-400 py-200 text-[13px] font-medium text-brand-primary"
        >
          {label}
        </button>
      )}
      {error ? (
        <p className="mt-200 text-[12px] text-state-danger">{error}</p>
      ) : null}
    </div>
  );
}

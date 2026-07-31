'use client';

/**
 * Client-side create-draw form. Posts to /api/admin/draws (the
 * cookie-aware proxy) which forwards to POST /api/v1/draws.
 */

import { useRouter } from 'next/navigation';
import { type FormEvent, useState } from 'react';

interface Props {
  onCreated?: () => void;
}

export default function NewDrawForm({ onCreated }: Props) {
  const router = useRouter();
  const [prize, setPrize] = useState('');
  const [priceMinor, setPriceMinor] = useState('50000');
  const [closeTime, setCloseTime] = useState('');
  const [drawTime, setDrawTime] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    const response = await fetch('/api/admin/draws', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prize_copy: prize,
        ticket_price_minor: Number(priceMinor),
        close_time: new Date(closeTime).toISOString(),
        draw_time: new Date(drawTime).toISOString(),
      }),
    });
    setSubmitting(false);
    if (!response.ok) {
      const body = (await response.json().catch(() => ({}))) as {
        message?: string;
        error?: string;
      };
      setError(body.message ?? body.error ?? 'Failed to create draw.');
      return;
    }
    setPrize('');
    setCloseTime('');
    setDrawTime('');
    onCreated?.();
    router.refresh();
  }

  return (
    <form
      onSubmit={onSubmit}
      className="rounded-large border border-divider-hairline bg-surface-elevated p-600"
    >
      <h3 className="font-display text-[20px] font-semibold text-text-primary">
        Create new draw
      </h3>
      <div className="mt-400 grid gap-400 md:grid-cols-2">
        <label className="flex flex-col text-[13px] text-text-secondary md:col-span-2">
          Prize copy
          <input
            required
            value={prize}
            onChange={(e) => setPrize(e.target.value)}
            placeholder="Win ₦2M cash or a Lagos apartment."
            className="mt-100 rounded border border-divider-strong bg-surface-base px-300 py-200 text-[14px] text-text-primary"
          />
        </label>
        <label className="flex flex-col text-[13px] text-text-secondary">
          Ticket price (kobo)
          <input
            required
            type="number"
            min="1"
            value={priceMinor}
            onChange={(e) => setPriceMinor(e.target.value)}
            className="mt-100 rounded border border-divider-strong bg-surface-base px-300 py-200 text-[14px] text-text-primary"
          />
        </label>
        <label className="flex flex-col text-[13px] text-text-secondary">
          &nbsp;
          <span className="mt-100 rounded border border-transparent px-300 py-200 text-[12px] text-text-secondary">
            ₦{(Number(priceMinor || 0) / 100).toFixed(2)} per ticket
          </span>
        </label>
        <label className="flex flex-col text-[13px] text-text-secondary">
          Close time
          <input
            required
            type="datetime-local"
            value={closeTime}
            onChange={(e) => setCloseTime(e.target.value)}
            className="mt-100 rounded border border-divider-strong bg-surface-base px-300 py-200 text-[14px] text-text-primary"
          />
        </label>
        <label className="flex flex-col text-[13px] text-text-secondary">
          Draw time
          <input
            required
            type="datetime-local"
            value={drawTime}
            onChange={(e) => setDrawTime(e.target.value)}
            className="mt-100 rounded border border-divider-strong bg-surface-base px-300 py-200 text-[14px] text-text-primary"
          />
        </label>
      </div>
      {error ? (
        <p className="mt-400 rounded border border-state-danger bg-surface-base p-300 text-[13px] text-state-danger">
          {error}
        </p>
      ) : null}
      <button
        type="submit"
        disabled={submitting}
        className="mt-400 rounded bg-brand-primary px-400 py-200 text-[14px] font-medium text-text-inverted disabled:opacity-60"
      >
        {submitting ? 'Creating…' : 'Create draw'}
      </button>
    </form>
  );
}

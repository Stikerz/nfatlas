'use client';

import type { ReactNode } from 'react';
import { useCallback, useEffect, useId, useMemo, useRef, useState } from 'react';
import { createPortal } from 'react-dom';

import { Button } from './Button';

/**
 * Modal — centred dialog for confirmations and focused interactions.
 * Every irreversible action (Cancel, Publish, Close, Reveal, Export) goes
 * through this per components.md §15.
 *
 * Portal target: appended to <body> so the modal escapes container overflow
 * clipping. Backdrop uses surface-inverted at 60% opacity (warm-tinted per
 * tokens.md §5, not pure black).
 */
export interface ModalCta {
  label: string;
  onClick: () => void;
  loading?: boolean;
}

export interface ModalProps {
  open: boolean;
  headline: string;
  body: ReactNode;
  primaryCta: ModalCta;
  secondaryCta: ModalCta;
  eyebrow?: string;
  dismissOnBackdrop?: boolean;
  dismissOnEscape?: boolean;
  typeToConfirm?: string;
  primaryVariant?: 'primary' | 'danger';
}

export function Modal({
  open,
  headline,
  body,
  primaryCta,
  secondaryCta,
  eyebrow,
  dismissOnBackdrop = true,
  dismissOnEscape = true,
  typeToConfirm,
  primaryVariant = 'primary',
}: ModalProps) {
  const headlineId = useId();
  const confirmHintId = useId();
  const dialogRef = useRef<HTMLDivElement>(null);
  const returnFocusRef = useRef<Element | null>(null);
  const [confirmValue, setConfirmValue] = useState('');
  const [mounted, setMounted] = useState(false);

  const confirmMatched = useMemo(
    () => (typeToConfirm ? confirmValue === typeToConfirm : true),
    [typeToConfirm, confirmValue],
  );

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!open) return;
    returnFocusRef.current = document.activeElement;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    return () => {
      document.body.style.overflow = previousOverflow;
      if (returnFocusRef.current instanceof HTMLElement) {
        returnFocusRef.current.focus();
      }
    };
  }, [open]);

  useEffect(() => {
    if (!open) return;
    const first = dialogRef.current?.querySelector<HTMLElement>(
      'input, button, [href], [tabindex]:not([tabindex="-1"])',
    );
    first?.focus();
  }, [open]);

  const handleKeyDown = useCallback(
    (event: React.KeyboardEvent<HTMLDivElement>) => {
      if (dismissOnEscape && event.key === 'Escape') {
        event.preventDefault();
        secondaryCta.onClick();
      }
      if (event.key === 'Tab') {
        const focusables = dialogRef.current?.querySelectorAll<HTMLElement>(
          'input:not([disabled]), button:not([disabled]), [href], [tabindex]:not([tabindex="-1"])',
        );
        if (!focusables || focusables.length === 0) return;
        const first = focusables[0];
        const last = focusables[focusables.length - 1];
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first.focus();
        }
      }
    },
    [dismissOnEscape, secondaryCta],
  );

  if (!open || !mounted) return null;

  const overlay = (
    <div
      className="fixed inset-0 z-[110] flex items-center justify-center bg-surface-inverted/60 px-400"
      onClick={dismissOnBackdrop ? secondaryCta.onClick : undefined}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby={headlineId}
        ref={dialogRef}
        onClick={(e) => e.stopPropagation()}
        onKeyDown={handleKeyDown}
        className="w-full max-w-[520px] rounded-large bg-surface-base p-800 shadow-e2"
      >
        {eyebrow ? (
          <p className="text-[12px] font-medium uppercase tracking-[0.05em] text-brand-accent">
            {eyebrow}
          </p>
        ) : null}
        <h2
          id={headlineId}
          className="mt-200 font-display text-[24px] font-semibold leading-[1.2] text-text-primary"
        >
          {headline}
        </h2>
        <div className="mt-400 font-body text-[16px] leading-[1.6] text-text-primary">
          {body}
        </div>
        {typeToConfirm ? (
          <div className="mt-600">
            <label className="text-[14px] leading-[1.5] text-text-secondary">
              Type <span className="font-mono">{typeToConfirm}</span> to confirm
            </label>
            <input
              type="text"
              autoComplete="off"
              value={confirmValue}
              onChange={(e) => setConfirmValue(e.target.value)}
              aria-describedby={confirmHintId}
              className="mt-200 h-[48px] w-full rounded-small border border-divider-hairline px-300 text-[16px] leading-[1.6] text-text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-focus focus-visible:ring-offset-[1px]"
            />
            <p
              id={confirmHintId}
              aria-live="polite"
              className="mt-100 text-[14px] leading-[1.5] text-text-secondary"
            >
              {confirmMatched ? 'Confirmation matched.' : 'Confirmation not yet matched.'}
            </p>
          </div>
        ) : null}
        <div className="mt-800 flex items-center justify-end gap-300">
          <Button
            label={secondaryCta.label}
            variant="secondary"
            onClick={secondaryCta.onClick}
          />
          <Button
            label={primaryCta.label}
            variant={primaryVariant}
            loading={primaryCta.loading}
            disabled={!confirmMatched}
            onClick={primaryCta.onClick}
          />
        </div>
      </div>
    </div>
  );

  return createPortal(overlay, document.body);
}

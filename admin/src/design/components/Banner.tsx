'use client';

import type { ReactNode } from 'react';

/**
 * Banner — top-of-content region notification.
 * Spec: `_bmad-output/planning-artifacts/design/components.md §9`.
 */
export type BannerVariant = 'info' | 'success' | 'attention' | 'danger';

export interface BannerAction {
  label: string;
  onClick: () => void;
}

export interface BannerProps {
  body: string | ReactNode;
  variant?: BannerVariant;
  headline?: string;
  dismissible?: boolean;
  onDismiss?: () => void;
  actions?: BannerAction[];
}

const ACCENT: Record<BannerVariant, { bg: string; border: string; text: string }> = {
  info: {
    bg: 'bg-brand-primary/[.12]',
    border: 'border-brand-primary',
    text: 'text-brand-primary',
  },
  success: {
    bg: 'bg-state-success/[.12]',
    border: 'border-state-success',
    text: 'text-state-success',
  },
  attention: {
    bg: 'bg-state-attention/[.12]',
    border: 'border-state-attention',
    text: 'text-state-attention',
  },
  danger: {
    bg: 'bg-state-danger/[.12]',
    border: 'border-state-danger',
    text: 'text-state-danger',
  },
};

export function Banner({
  body,
  variant = 'info',
  headline,
  dismissible = true,
  onDismiss,
  actions,
}: BannerProps) {
  const accent = ACCENT[variant];
  const role = variant === 'danger' || variant === 'attention' ? 'alert' : 'status';

  return (
    <div
      role={role}
      className={`flex items-start gap-400 rounded-medium border-l-[4px] p-400 ${accent.bg} ${accent.border}`}
    >
      <div className="flex-1">
        {headline ? (
          <p className={`font-body text-[16px] font-semibold leading-[1.6] ${accent.text}`}>
            {headline}
          </p>
        ) : null}
        <div className={`font-body text-[16px] leading-[1.6] ${accent.text}`}>{body}</div>
        {actions && actions.length > 0 ? (
          <div className="mt-300 flex flex-wrap gap-300">
            {actions.map((action) => (
              <button
                key={action.label}
                type="button"
                onClick={action.onClick}
                className={`font-body text-[15px] font-medium underline underline-offset-2 ${accent.text}`}
              >
                {action.label}
              </button>
            ))}
          </div>
        ) : null}
      </div>
      {dismissible && onDismiss ? (
        <button
          type="button"
          onClick={onDismiss}
          aria-label="Dismiss"
          className={`inline-flex h-[24px] w-[24px] items-center justify-center rounded-small ${accent.text} hover:bg-surface-subtle focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-focus focus-visible:ring-offset-[2px]`}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path
              d="M6 6l12 12M18 6L6 18"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </svg>
        </button>
      ) : null}
    </div>
  );
}

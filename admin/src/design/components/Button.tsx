'use client';

import type { ButtonHTMLAttributes, ReactNode } from 'react';

/**
 * Button — the default interactive commitment element.
 * Spec: `_bmad-output/planning-artifacts/design/components.md §3`.
 */
export type ButtonVariant = 'primary' | 'secondary' | 'danger';
export type ButtonSize = 'medium' | 'large';
export type ButtonWidth = 'auto' | 'full';

export interface ButtonProps extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'children'> {
  label: string;
  variant?: ButtonVariant;
  size?: ButtonSize;
  width?: ButtonWidth;
  loading?: boolean;
  loadingLabel?: string;
  leadingIcon?: ReactNode;
  trailingIcon?: ReactNode;
  /** §3.4 bounded exception: primary variant only, irreversible-action pattern. */
  attentionHint?: boolean;
}

const BASE =
  'inline-flex items-center justify-center gap-200 rounded-medium font-body text-[15px] font-medium leading-[1.2] transition-[background-color,color,border-color] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-focus focus-visible:ring-offset-[3px]';

const SIZE: Record<ButtonSize, string> = {
  medium: 'h-[48px] px-400',
  large: 'h-[52px] px-600',
};

const VARIANT: Record<ButtonVariant, string> = {
  primary:
    'bg-brand-primary text-text-inverted hover:brightness-110 active:bg-brand-primary/95 disabled:bg-surface-elevated disabled:text-text-secondary',
  secondary:
    'bg-transparent border border-brand-primary text-brand-primary hover:bg-surface-subtle disabled:border-text-secondary disabled:text-text-secondary',
  danger:
    'bg-transparent text-state-danger hover:bg-surface-subtle disabled:text-text-secondary',
};

const ATTENTION_HINT =
  'relative before:content-[""] before:absolute before:inset-0 before:rounded-medium before:bg-state-attention/[.12] before:pointer-events-none';

export function Button({
  label,
  variant = 'primary',
  size = 'medium',
  width = 'auto',
  loading = false,
  loadingLabel,
  leadingIcon,
  trailingIcon,
  attentionHint = false,
  disabled,
  className,
  type = 'button',
  ...rest
}: ButtonProps) {
  const effectivelyDisabled = disabled || loading;
  const classes = [
    BASE,
    SIZE[size],
    VARIANT[variant],
    width === 'full' ? 'w-full' : '',
    attentionHint && variant === 'primary' && !effectivelyDisabled ? ATTENTION_HINT : '',
    className ?? '',
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <button
      type={type}
      className={classes}
      aria-disabled={effectivelyDisabled || undefined}
      aria-busy={loading || undefined}
      disabled={effectivelyDisabled}
      {...rest}
    >
      {loading ? (
        <>
          <Spinner />
          {loadingLabel ? <span>{loadingLabel}</span> : null}
        </>
      ) : (
        <>
          {leadingIcon ? (
            <span aria-hidden="true" className="inline-flex">
              {leadingIcon}
            </span>
          ) : null}
          <span>{label}</span>
          {trailingIcon ? (
            <span aria-hidden="true" className="inline-flex">
              {trailingIcon}
            </span>
          ) : null}
        </>
      )}
    </button>
  );
}

function Spinner() {
  return (
    <svg
      className="animate-spin"
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
    >
      <circle
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="3"
        strokeOpacity="0.25"
      />
      <path
        d="M22 12a10 10 0 0 0-10-10"
        stroke="currentColor"
        strokeWidth="3"
        strokeLinecap="round"
      />
    </svg>
  );
}

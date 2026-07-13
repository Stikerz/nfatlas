'use client';

import type { ChangeEvent, InputHTMLAttributes, ReactNode } from 'react';
import { useCallback, useId, useMemo, useState } from 'react';

/**
 * Input — every field the user types into.
 * Spec: `_bmad-output/planning-artifacts/design/components.md §4`.
 */
export type InputVariant = 'text' | 'password' | 'number' | 'phone' | 'date' | 'otp';

export interface InputProps
  extends Omit<
    InputHTMLAttributes<HTMLInputElement>,
    'onChange' | 'type' | 'value' | 'defaultValue'
  > {
  label: string;
  onChange: (value: string) => void;
  variant?: InputVariant;
  value?: string;
  placeholder?: string;
  helper?: string;
  required?: boolean;
  error?: string;
  readOnlyVerified?: boolean;
  otpLength?: number;
  showPasswordToggle?: boolean;
  leadingSlot?: ReactNode;
  trailingSlot?: ReactNode;
}

export function Input({
  label,
  onChange,
  variant = 'text',
  value,
  placeholder,
  helper,
  required = false,
  error,
  disabled = false,
  readOnlyVerified = false,
  otpLength = 6,
  showPasswordToggle = true,
  leadingSlot,
  trailingSlot,
  autoComplete,
  ...rest
}: InputProps) {
  const id = useId();
  const helperId = `${id}-helper`;
  const errorId = `${id}-error`;
  const [passwordVisible, setPasswordVisible] = useState(false);

  const handleChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>) => {
      onChange(event.target.value);
    },
    [onChange],
  );

  const inputType = useMemo(() => {
    if (variant === 'password') return passwordVisible ? 'text' : 'password';
    if (variant === 'number' || variant === 'otp') return 'text';
    if (variant === 'date') return 'date';
    if (variant === 'phone') return 'tel';
    return 'text';
  }, [variant, passwordVisible]);

  const inputMode = useMemo(() => {
    if (variant === 'number' || variant === 'otp') return 'numeric' as const;
    if (variant === 'phone') return 'tel' as const;
    return 'text' as const;
  }, [variant]);

  const describedBy = [helper ? helperId : null, error ? errorId : null]
    .filter(Boolean)
    .join(' ')
    .trim();

  const baseFieldClasses =
    'h-[48px] w-full rounded-small border bg-surface-base px-300 text-[16px] leading-[1.6] text-text-primary placeholder:text-text-secondary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-focus focus-visible:ring-offset-[1px] disabled:bg-surface-elevated disabled:cursor-not-allowed';
  const borderClasses = error
    ? 'border-state-danger'
    : 'border-divider-hairline';

  return (
    <div className="flex flex-col gap-100">
      <label
        htmlFor={id}
        className="text-[12px] font-medium leading-[1.3] uppercase tracking-[0.05em] text-text-secondary"
      >
        {required ? <span className="text-brand-accent mr-100">▪</span> : null}
        {label}
      </label>

      {variant === 'otp' ? (
        <input
          id={id}
          inputMode="numeric"
          pattern="[0-9]*"
          autoComplete="one-time-code"
          maxLength={otpLength}
          aria-required={required || undefined}
          aria-invalid={error ? true : undefined}
          aria-describedby={describedBy || undefined}
          disabled={disabled}
          value={value ?? ''}
          onChange={handleChange}
          placeholder={'·'.repeat(otpLength)}
          className={`${baseFieldClasses} ${borderClasses} text-center tracking-[0.5em] font-display text-[24px] leading-[1.2]`}
          {...rest}
        />
      ) : variant === 'phone' ? (
        <div className={`flex items-stretch rounded-small border ${error ? 'border-state-danger' : 'border-divider-hairline'} focus-within:ring-2 focus-within:ring-focus focus-within:ring-offset-[1px]`}>
          <span
            className="inline-flex items-center bg-surface-elevated px-300 rounded-l-small border-r border-divider-hairline text-text-primary"
            aria-hidden="true"
          >
            +234
          </span>
          <input
            id={id}
            type="tel"
            inputMode="tel"
            autoComplete={autoComplete ?? 'tel-national'}
            aria-required={required || undefined}
            aria-invalid={error ? true : undefined}
            aria-describedby={describedBy || undefined}
            disabled={disabled}
            value={value ?? ''}
            onChange={handleChange}
            placeholder={placeholder ?? '8030000000'}
            className="h-[46px] flex-1 rounded-r-small bg-surface-base px-300 text-[16px] leading-[1.6] text-text-primary placeholder:text-text-secondary focus:outline-none disabled:bg-surface-elevated"
            {...rest}
          />
        </div>
      ) : (
        <div className="relative">
          <input
            id={id}
            type={inputType}
            inputMode={inputMode}
            autoComplete={autoComplete}
            aria-required={required || undefined}
            aria-invalid={error ? true : undefined}
            aria-describedby={describedBy || undefined}
            disabled={disabled || readOnlyVerified}
            readOnly={readOnlyVerified}
            value={value ?? ''}
            onChange={handleChange}
            placeholder={placeholder}
            className={`${baseFieldClasses} ${borderClasses} ${(variant === 'password' && showPasswordToggle) || readOnlyVerified || trailingSlot ? 'pr-1200' : ''} ${leadingSlot ? 'pl-1200' : ''}`}
            {...rest}
          />
          {leadingSlot ? (
            <span className="absolute left-300 top-1/2 -translate-y-1/2 text-text-secondary" aria-hidden="true">
              {leadingSlot}
            </span>
          ) : null}
          {variant === 'password' && showPasswordToggle ? (
            <button
              type="button"
              className="absolute right-300 top-1/2 -translate-y-1/2 text-text-secondary hover:text-text-primary"
              aria-label={passwordVisible ? 'Hide password' : 'Show password'}
              onClick={() => setPasswordVisible((v) => !v)}
            >
              {passwordVisible ? '\u{1F441}\u{FE0F}' : '\u{1F441}‍\u{1F5E8}'}
            </button>
          ) : readOnlyVerified ? (
            <span className="absolute right-300 top-1/2 -translate-y-1/2 inline-flex items-center gap-100 rounded-small bg-state-success/10 px-200 py-100">
              <span aria-hidden="true">✓</span>
              <span className="text-[12px] font-medium uppercase tracking-[0.05em] text-state-success">
                verified
              </span>
            </span>
          ) : trailingSlot ? (
            <span className="absolute right-300 top-1/2 -translate-y-1/2 text-text-secondary" aria-hidden="true">
              {trailingSlot}
            </span>
          ) : null}
        </div>
      )}

      {error ? (
        <p
          id={errorId}
          role="alert"
          aria-live="polite"
          className="text-[14px] leading-[1.5] text-state-danger"
        >
          {error}
        </p>
      ) : helper ? (
        <p id={helperId} className="text-[14px] leading-[1.5] text-text-secondary">
          {helper}
        </p>
      ) : null}
    </div>
  );
}

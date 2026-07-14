'use client';

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react';
import type { ReactNode } from 'react';
import { createPortal } from 'react-dom';

/**
 * Toast — ephemeral notification of a completed micro-action.
 * Spec: `_bmad-output/planning-artifacts/design/components.md §16`.
 *
 * Usage: wrap the admin shell in <ToastProvider/> once (root layout), then
 * call `useToast()` in any client component. Stack cap is 3 visible; older
 * toasts auto-dismiss when a fourth arrives.
 */
export type ToastVariant = 'default' | 'success' | 'attention' | 'danger';

export interface ToastOptions {
  variant?: ToastVariant;
  duration?: number;
}

interface ToastEntry {
  id: number;
  message: string;
  variant: ToastVariant;
  duration: number;
}

interface ToastContextValue {
  show: (message: string, opts?: ToastOptions) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

const STACK_LIMIT = 3;

const DEFAULT_DURATION: Record<ToastVariant, number> = {
  default: 3000,
  success: 3000,
  attention: 3000,
  danger: 5000,
};

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastEntry[]>([]);
  const nextIdRef = useRef(1);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const dismiss = useCallback((id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const show = useCallback((message: string, opts?: ToastOptions) => {
    const variant = opts?.variant ?? 'default';
    const duration = opts?.duration ?? DEFAULT_DURATION[variant];
    const id = nextIdRef.current++;
    setToasts((prev) => {
      const next = [...prev, { id, message, variant, duration }];
      if (next.length > STACK_LIMIT) next.shift();
      return next;
    });
  }, []);

  const value = useMemo(() => ({ show }), [show]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      {mounted
        ? createPortal(
            <div className="fixed top-400 right-400 z-[200] flex flex-col gap-200 pointer-events-none">
              {toasts.map((t) => (
                <ToastItem key={t.id} entry={t} onDismiss={() => dismiss(t.id)} />
              ))}
            </div>,
            document.body,
          )
        : null}
    </ToastContext.Provider>
  );
}

export function useToast(): ToastContextValue {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast() must be used inside <ToastProvider/>');
  return ctx;
}

function ToastItem({
  entry,
  onDismiss,
}: {
  entry: ToastEntry;
  onDismiss: () => void;
}) {
  useEffect(() => {
    const timer = window.setTimeout(onDismiss, entry.duration);
    return () => window.clearTimeout(timer);
  }, [entry.duration, onDismiss]);

  const isDanger = entry.variant === 'danger';
  const role = isDanger ? 'alert' : 'status';
  const bg = isDanger ? 'bg-state-danger' : 'bg-surface-inverted';
  const iconColour: Record<ToastVariant, string> = {
    default: '',
    success: 'text-state-success',
    attention: 'text-state-attention',
    danger: '',
  };

  return (
    <div
      role={role}
      aria-live={isDanger ? 'assertive' : 'polite'}
      className={`pointer-events-auto flex items-center gap-200 rounded-medium ${bg} px-400 py-300 text-text-inverted font-body text-[14px] leading-[1.5] shadow-e2`}
    >
      {entry.variant === 'success' ? (
        <span aria-hidden="true" className={iconColour.success}>
          ✓
        </span>
      ) : null}
      {entry.variant === 'attention' ? (
        <span aria-hidden="true" className={iconColour.attention}>
          ⚠
        </span>
      ) : null}
      <span>{entry.message}</span>
      {isDanger ? (
        <button
          type="button"
          onClick={onDismiss}
          aria-label="Dismiss"
          className="ml-200 inline-flex h-[20px] w-[20px] items-center justify-center rounded-small hover:bg-white/10"
        >
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" aria-hidden="true">
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

'use client';

import { useRouter } from 'next/navigation';
import { useState } from 'react';

import { Banner } from '@/design/components/Banner';
import { Button } from '@/design/components/Button';
import { Input } from '@/design/components/Input';

/**
 * wf-08 Screen 8.1 — Admin login.
 * Spec: `_bmad-output/planning-artifacts/design/wireframes/08-admin-login.md §2`.
 */
export default function AdminLoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [forgotToast, setForgotToast] = useState(false);

  const canSubmit = email.length > 0 && password.length > 0 && !busy;

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canSubmit) return;
    setBusy(true);
    setError(null);
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      if (!response.ok) {
        const body = (await response.json().catch(() => null)) as
          | { code?: string; message?: string }
          | null;
        setError(body?.message ?? "That combination didn't work. Try again.");
        setPassword('');
        setBusy(false);
        return;
      }
      router.replace('/admin');
    } catch {
      setError("We couldn't sign you in. Try again in a moment.");
      setBusy(false);
    }
  }

  return (
    <main className="min-h-screen bg-surface-base">
      <div className="flex min-h-screen flex-col items-center justify-between py-2400">
        <div className="w-full max-w-[440px] px-400">
          {error ? (
            <div className="mb-400">
              <Banner
                variant="danger"
                body={error}
                dismissible
                onDismiss={() => setError(null)}
              />
            </div>
          ) : null}
          {forgotToast ? (
            <div className="mb-400">
              <Banner
                variant="info"
                body="Password reset arrives with V1. Contact founder for now."
                dismissible
                onDismiss={() => setForgotToast(false)}
              />
            </div>
          ) : null}

          <form
            onSubmit={submit}
            className="rounded-large bg-surface-elevated p-[40px] shadow-e1"
          >
            <h1 className="font-display text-[24px] font-semibold leading-[1.2] text-text-primary">
              Atlas Admin
            </h1>
            <p className="mt-400 text-[16px] leading-[1.6] text-text-secondary">
              Sign in to operate draws, review claims, and inspect the audit log.
            </p>

            <div className="my-600 border-t border-divider-hairline" />

            <div className="flex flex-col gap-400">
              <Input
                label="Email"
                placeholder="operator@atlas.ng"
                autoComplete="username"
                value={email}
                onChange={setEmail}
              />
              <Input
                label="Password"
                variant="password"
                autoComplete="current-password"
                value={password}
                onChange={setPassword}
              />
            </div>

            <div className="mt-600">
              <Button
                type="submit"
                label={busy ? 'Signing in…' : 'Sign in'}
                size="large"
                width="full"
                loading={busy}
                disabled={!canSubmit}
              />
            </div>

            <div className="my-600 border-t border-divider-hairline" />

            <button
              type="button"
              onClick={() => setForgotToast(true)}
              className="text-[16px] font-medium text-brand-primary underline underline-offset-2"
            >
              Forgot your password?
            </button>
          </form>
        </div>

        <p className="mt-2400 text-[14px] leading-[1.5] text-text-secondary">
          Atlas Africa Ltd — V0.5 demo build — {new Date().toISOString().slice(0, 10)}
        </p>
      </div>
    </main>
  );
}

/**
 * Session cookie helpers for the admin app.
 *
 * The backend issues a JWT for the operator session; we store it in an
 * httpOnly cookie so client JS can never read it (XSS-safe). Every
 * admin-side backend call goes through server-side Route Handlers which
 * read the cookie and pass it as Authorization: Bearer to the backend.
 *
 * Cookie name deliberately distinct from any consumer-app equivalent —
 * the admin surface is a separate origin in prod (admin.atlas.ng vs
 * atlas.ng) but development runs both on localhost, so the name prevents
 * collisions.
 */

import type { cookies as CookiesFn } from 'next/headers';

export const ADMIN_SESSION_COOKIE = '__atlas_admin_session';

const SESSION_TTL_SECONDS = Number(process.env.ATLAS_SESSION_TTL_HOURS ?? 8) * 60 * 60;

type Cookies = Awaited<ReturnType<typeof CookiesFn>>;

export function readAdminToken(cookies: Cookies): string | null {
  const cookie = cookies.get(ADMIN_SESSION_COOKIE);
  return cookie?.value ?? null;
}

export function writeAdminToken(cookies: Cookies, token: string): void {
  cookies.set({
    name: ADMIN_SESSION_COOKIE,
    value: token,
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    path: '/',
    maxAge: SESSION_TTL_SECONDS,
  });
}

export function clearAdminToken(cookies: Cookies): void {
  cookies.set({
    name: ADMIN_SESSION_COOKIE,
    value: '',
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    path: '/',
    maxAge: 0,
  });
}

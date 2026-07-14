import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

import { ADMIN_SESSION_COOKIE } from './src/lib/session';

/**
 * Auth guard: any request under /admin without a session cookie is
 * redirected to /login. Bearer validity itself is enforced by the backend
 * (each /api/* Route Handler re-checks); the cookie presence check here
 * is just to avoid rendering the operator shell for anonymous visitors.
 *
 * /login is always accessible; the login handler will redirect to /admin
 * on the client after a successful POST /api/auth/login.
 */
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  const cookie = request.cookies.get(ADMIN_SESSION_COOKIE);
  const authenticated = Boolean(cookie?.value);

  if (pathname === '/') {
    return NextResponse.redirect(
      new URL(authenticated ? '/admin' : '/login', request.url),
    );
  }

  if ((pathname === '/admin' || pathname.startsWith('/admin/')) && !authenticated) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  if (pathname === '/login' && authenticated) {
    return NextResponse.redirect(new URL('/admin', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/', '/admin/:path*', '/login'],
};

import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';

import { atlasFetch } from '@/lib/api-client';
import { clearAdminToken, readAdminToken } from '@/lib/session';

interface BackendSessionCurrent {
  is_admin: boolean;
  roles: string[];
  user_id: string;
  email: string;
  session_id: string;
  expires_at: string;
}

export async function GET() {
  const store = await cookies();
  const token = readAdminToken(store);

  if (!token) {
    return NextResponse.json({ authenticated: false }, { status: 401 });
  }

  const current = await atlasFetch<BackendSessionCurrent>(
    '/api/v1/sessions/current',
    { bearerToken: token },
  );

  if (!current.ok || !current.body) {
    // Token invalid / revoked — clear cookie so subsequent loads route to login.
    clearAdminToken(store);
    return NextResponse.json({ authenticated: false }, { status: 401 });
  }

  if (!current.body.is_admin) {
    clearAdminToken(store);
    return NextResponse.json(
      { authenticated: false, reason: 'not_operator' },
      { status: 403 },
    );
  }

  return NextResponse.json({
    authenticated: true,
    user_id: current.body.user_id,
    email: current.body.email,
    roles: current.body.roles,
    session_id: current.body.session_id,
    expires_at: current.body.expires_at,
  });
}

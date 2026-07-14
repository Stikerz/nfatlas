import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';

import { atlasFetch } from '@/lib/api-client';
import { writeAdminToken } from '@/lib/session';

interface LoginBody {
  email?: string;
  password?: string;
}

interface BackendSessionCreate {
  session_id: string;
  user_id: string;
  access_token: string;
  expires_at: string;
}

interface BackendSessionCurrent {
  is_admin: boolean;
  roles: string[];
  user_id: string;
  email: string;
  expires_at: string;
}

export async function POST(request: Request) {
  const { email, password } = (await request.json()) as LoginBody;

  if (!email || !password) {
    return NextResponse.json(
      { code: 'missing_fields', message: 'Email and password are required.' },
      { status: 400 },
    );
  }

  const login = await atlasFetch<BackendSessionCreate>('/api/v1/sessions', {
    method: 'POST',
    body: { email, password },
  });

  if (!login.ok || !login.body) {
    return NextResponse.json(
      {
        code: login.errorCode ?? 'invalid_credentials',
        message:
          login.errorMessage ?? "That combination didn't work. Try again.",
      },
      { status: login.status || 401 },
    );
  }

  const token = login.body.access_token;

  // Confirm the user has the superadmin role before setting the cookie.
  const current = await atlasFetch<BackendSessionCurrent>(
    '/api/v1/sessions/current',
    { bearerToken: token },
  );
  if (!current.ok || !current.body?.is_admin) {
    // Revoke the just-issued session immediately — no operator access.
    await atlasFetch<null>('/api/v1/sessions/current/logout', {
      method: 'POST',
      bearerToken: token,
    });
    return NextResponse.json(
      {
        code: 'not_operator',
        message:
          'This account does not have operator access. Contact the founder.',
      },
      { status: 403 },
    );
  }

  writeAdminToken(await cookies(), token);
  return NextResponse.json({
    user_id: current.body.user_id,
    email: current.body.email,
    roles: current.body.roles,
    expires_at: current.body.expires_at,
  });
}

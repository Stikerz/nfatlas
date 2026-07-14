import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';

import { atlasFetch } from '@/lib/api-client';
import { clearAdminToken, readAdminToken } from '@/lib/session';

export async function POST() {
  const store = await cookies();
  const token = readAdminToken(store);

  if (token) {
    // Best effort — even if the backend refuses, we still clear the cookie.
    await atlasFetch<null>('/api/v1/sessions/current/logout', {
      method: 'POST',
      bearerToken: token,
    });
  }

  clearAdminToken(store);
  return NextResponse.json({ ok: true });
}

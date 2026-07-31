/**
 * Admin draws proxy — POST creates a new draw, GET lists active.
 *
 * Client components can't send Authorization headers safely (the
 * bearer lives in an httpOnly cookie), so they call this route
 * which unwraps the cookie server-side and forwards to the backend.
 */

import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';

import { atlasFetch } from '@/lib/api-client';
import { readAdminToken } from '@/lib/session';

interface CreateDrawBody {
  prize_copy: string;
  ticket_price_minor: number;
  close_time: string;
  draw_time: string;
  entries_cap?: number | null;
}

export async function POST(request: Request) {
  const store = await cookies();
  const token = readAdminToken(store);
  if (!token) {
    return NextResponse.json({ error: 'unauthenticated' }, { status: 401 });
  }

  let body: CreateDrawBody;
  try {
    body = (await request.json()) as CreateDrawBody;
  } catch {
    return NextResponse.json({ error: 'invalid_body' }, { status: 400 });
  }

  const response = await atlasFetch<unknown>('/api/v1/draws', {
    method: 'POST',
    bearerToken: token,
    body,
  });

  if (!response.ok) {
    return NextResponse.json(
      { error: response.errorCode ?? 'create_failed', message: response.errorMessage },
      { status: response.status },
    );
  }
  return NextResponse.json(response.body, { status: 201 });
}

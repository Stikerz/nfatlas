import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';

import { atlasFetch } from '@/lib/api-client';
import { readAdminToken } from '@/lib/session';

export async function POST(
  _request: Request,
  { params }: { params: Promise<{ drawId: string }> },
) {
  const { drawId } = await params;
  const store = await cookies();
  const token = readAdminToken(store);
  if (!token) return NextResponse.json({ error: 'unauthenticated' }, { status: 401 });

  const response = await atlasFetch<unknown>(`/api/v1/draws/${drawId}/reveal`, {
    method: 'POST',
    bearerToken: token,
    body: {},
  });
  if (!response.ok) {
    return NextResponse.json(
      { error: response.errorCode ?? 'reveal_failed', message: response.errorMessage },
      { status: response.status },
    );
  }
  return NextResponse.json(response.body, { status: 200 });
}

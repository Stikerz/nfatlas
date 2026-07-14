/**
 * Server-side fetch wrapper around the Atlas backend.
 *
 * Only imported from Next.js Route Handlers / Server Components — the
 * bearer token lives in an httpOnly cookie and is unreachable from client
 * JavaScript by design. Client components call the Next.js /api/*
 * handlers, which internally use this wrapper.
 *
 * The idempotency-key generation matches the Flutter interceptor:
 * every POST/PUT/PATCH/DELETE gets a fresh randomUUID unless the caller
 * provides one explicitly.
 */

const IDEMPOTENT_METHODS = new Set(['POST', 'PUT', 'PATCH', 'DELETE']);

const DEFAULT_BASE_URL = process.env.ATLAS_API_BASE_URL ?? 'http://backend:8000';

export interface AtlasResponse<T> {
  ok: boolean;
  status: number;
  body: T | null;
  errorCode?: string;
  errorMessage?: string;
}

export interface AtlasRequestInit extends Omit<RequestInit, 'headers' | 'body'> {
  headers?: Record<string, string>;
  body?: unknown;
  bearerToken?: string | null;
  idempotencyKey?: string;
}

export async function atlasFetch<T>(
  path: string,
  init: AtlasRequestInit = {},
): Promise<AtlasResponse<T>> {
  const method = (init.method ?? 'GET').toUpperCase();
  const headers = new Headers(init.headers ?? {});
  if (!headers.has('Content-Type') && init.body !== undefined) {
    headers.set('Content-Type', 'application/json');
  }
  if (init.bearerToken && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${init.bearerToken}`);
  }
  if (IDEMPOTENT_METHODS.has(method) && !headers.has('Idempotency-Key')) {
    headers.set('Idempotency-Key', init.idempotencyKey ?? crypto.randomUUID());
  }

  const url = new URL(path, DEFAULT_BASE_URL).toString();
  const response = await fetch(url, {
    ...init,
    method,
    headers,
    body: init.body !== undefined ? JSON.stringify(init.body) : undefined,
    cache: 'no-store',
  });

  let body: T | null = null;
  const text = await response.text();
  if (text) {
    try {
      body = JSON.parse(text) as T;
    } catch {
      body = null;
    }
  }

  if (!response.ok) {
    const detail = extractDetail(body);
    return {
      ok: false,
      status: response.status,
      body,
      errorCode: detail?.code,
      errorMessage: detail?.message,
    };
  }

  return { ok: true, status: response.status, body };
}

function extractDetail(body: unknown): { code?: string; message?: string } | null {
  if (body && typeof body === 'object' && 'detail' in body) {
    const detail = (body as { detail: unknown }).detail;
    if (detail && typeof detail === 'object') {
      return detail as { code?: string; message?: string };
    }
  }
  return null;
}

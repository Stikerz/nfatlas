import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';

import { AdminSidebar } from '@/design/components/Sidebar';
import { AdminTopBar } from '@/design/components/TopBar';
import { atlasFetch } from '@/lib/api-client';
import { readAdminToken } from '@/lib/session';

/**
 * Admin shell — wraps every /admin/* page in Sidebar + TopBar.
 * The server-side session check runs on every request; expired or revoked
 * tokens bounce to /login before any admin content renders.
 */
interface BackendSessionCurrent {
  is_admin: boolean;
  roles: string[];
  user_id: string;
  email: string;
  session_id: string;
  expires_at: string;
}

function operatorNameFromEmail(email: string): string {
  const local = email.split('@')[0];
  return local
    .split(/[._-]+/)
    .filter(Boolean)
    .map((part) => part[0].toUpperCase() + part.slice(1))
    .join(' ');
}

export default async function AdminLayout({ children }: { children: React.ReactNode }) {
  const token = readAdminToken(await cookies());
  if (!token) redirect('/login');

  const current = await atlasFetch<BackendSessionCurrent>('/api/v1/sessions/current', {
    bearerToken: token,
  });

  if (!current.ok || !current.body?.is_admin) {
    redirect('/login');
  }

  return (
    <div className="flex min-h-screen bg-surface-base">
      <AdminSidebar />
      <div className="flex flex-1 flex-col">
        <AdminTopBar operatorName={operatorNameFromEmail(current.body.email)} />
        <main className="mx-auto w-full max-w-[1280px] flex-1 px-600 py-600">
          {children}
        </main>
      </div>
    </div>
  );
}

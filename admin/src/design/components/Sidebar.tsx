'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

/**
 * AdminSidebar — operator surface primary navigation.
 * Spec: `_bmad-output/planning-artifacts/design/wireframes/08-admin-login.md §1.2`.
 *
 * Active state is a leading `→` arrow (not a background fill — restraint
 * over expressiveness per wf-08 §1.1). Section labels use type.label.micro
 * in gold; nav items use type.body.default; active item text weight bumps
 * to text.primary; inactive stays at text.secondary.
 */

interface NavItem {
  label: string;
  href?: string;
  counter?: string;
}

interface NavGroup {
  label: string;
  items: NavItem[];
}

const NAV_GROUPS: NavGroup[] = [
  {
    label: 'THIS WEEK',
    items: [
      { label: 'Draws', counter: '· —' },
      { label: 'Tickets', counter: '—' },
      { label: 'Claims', counter: '—' },
    ],
  },
  {
    label: 'OPERATE',
    items: [
      { label: 'Draws', href: '/admin/draws' },
      { label: 'Tickets', href: '/admin/tickets' },
      { label: 'Free entries', href: '/admin/free-entries' },
      { label: 'Claims', href: '/admin/claims' },
    ],
  },
  {
    label: 'REVIEW',
    items: [
      { label: 'Audit log', href: '/admin/audit-log' },
      { label: 'Users', href: '/admin/users' },
      { label: 'Compliance', href: '/admin/compliance' },
    ],
  },
  {
    label: 'SETTINGS',
    items: [
      { label: 'Skill questions', href: '/admin/skill-questions' },
      { label: 'V0.5 tools', href: '/admin/seed-tools' },
    ],
  },
];

export function AdminSidebar() {
  const pathname = usePathname();

  return (
    <nav
      aria-label="Operator navigation"
      className="w-[240px] shrink-0 border-r border-divider-hairline bg-surface-elevated px-400 py-600"
    >
      {NAV_GROUPS.map((group) => (
        <div key={group.label} className="mb-800">
          <p className="mb-300 text-[12px] font-medium uppercase tracking-[0.05em] text-brand-accent">
            <span className="mr-100 text-brand-accent">▪</span>
            {group.label}
          </p>
          <ul className="flex flex-col gap-100">
            {group.items.map((item) => {
              const active = item.href ? pathname === item.href : false;
              const inner = (
                <span
                  className={`flex items-center justify-between rounded-small px-300 py-200 text-[16px] leading-[1.6] ${
                    active
                      ? 'font-medium text-text-primary'
                      : 'text-text-secondary hover:bg-surface-subtle'
                  }`}
                >
                  <span>
                    {active ? (
                      <span aria-hidden="true" className="mr-200 text-text-primary">
                        →
                      </span>
                    ) : null}
                    {item.label}
                  </span>
                  {item.counter ? (
                    <span className="text-[14px] font-medium text-brand-accent">
                      {item.counter}
                    </span>
                  ) : null}
                </span>
              );
              return (
                <li key={`${group.label}-${item.label}`}>
                  {item.href ? (
                    <Link href={item.href}>{inner}</Link>
                  ) : (
                    <div className="cursor-default">{inner}</div>
                  )}
                </li>
              );
            })}
          </ul>
        </div>
      ))}
    </nav>
  );
}

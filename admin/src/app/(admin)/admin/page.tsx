/**
 * Admin dashboard — the "THIS WEEK" landing surface.
 * V0.5: empty state (no draws configured yet). Weeks 5-6 populate with
 * active-draw card + weekly counters.
 */
export default function AdminDashboardPage() {
  return (
    <div>
      <p className="text-[12px] font-medium uppercase tracking-[0.05em] text-brand-accent">
        ▪ This week
      </p>
      <h2 className="mt-200 font-display text-[32px] font-semibold leading-[1.15] text-text-primary">
        No active draws.
      </h2>
      <p className="mt-400 max-w-[560px] text-[16px] leading-[1.6] text-text-secondary">
        The dashboard populates as draws move through the create → publish → close →
        reveal lifecycle. Use <span className="font-medium">Operate → Draws</span> to
        create the first V0.5 demo draw, or load the seed data from{' '}
        <span className="font-medium">Settings → V0.5 tools</span>.
      </p>

      <section className="mt-1200 grid grid-cols-3 gap-600">
        {[
          { label: 'Draws', value: '—' },
          { label: 'Tickets', value: '—' },
          { label: 'Claims', value: '—' },
        ].map((stat) => (
          <div
            key={stat.label}
            className="rounded-large border border-divider-hairline bg-surface-elevated p-600"
          >
            <p className="text-[12px] font-medium uppercase tracking-[0.05em] text-text-secondary">
              {stat.label}
            </p>
            <p className="mt-200 font-display text-[40px] leading-[1.1] text-text-primary">
              {stat.value}
            </p>
          </div>
        ))}
      </section>
    </div>
  );
}

/**
 * Day 1 shell — proves tokens compile and the app boots on Chrome.
 * Real wf-08 admin login lands Day 5.
 */
export default function Page() {
  return (
    <main className="min-h-screen flex items-center justify-center bg-surface-base">
      <div className="max-w-md text-center px-800">
        <h1 className="font-display text-[40px] leading-[1.1] font-semibold text-text-primary">
          Atlas Admin
        </h1>
        <p className="mt-400 text-text-secondary">Day 1 shell — tokens loaded.</p>
      </div>
    </main>
  );
}

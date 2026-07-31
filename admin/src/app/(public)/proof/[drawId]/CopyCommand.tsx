'use client';

/**
 * Client island for the copy-to-clipboard verify command.
 *
 * The rest of the /proof page is SSR-only. This is the only interactive
 * element — a regulator can screenshot the page without JS and still
 * see the exact command they'd need to type manually.
 */

import { useState } from 'react';

interface Props {
  command: string;
}

export default function CopyCommand({ command }: Props) {
  const [copied, setCopied] = useState(false);

  const onClick = async () => {
    try {
      await navigator.clipboard.writeText(command);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      // Clipboard API blocked (e.g. non-secure context) — fall through
      // to the user copying manually from the visible <pre>.
    }
  };

  return (
    <div className="mt-3 flex items-start gap-2">
      <pre className="flex-1 overflow-x-auto rounded border border-[var(--color-border-subtle)] bg-[var(--color-bg-canvas)] p-3 font-mono text-xs">
        {command}
      </pre>
      <button
        type="button"
        onClick={onClick}
        className="rounded border border-[var(--color-border-strong)] bg-[var(--color-bg-surface)] px-3 py-2 text-xs font-medium hover:bg-[var(--color-bg-canvas)]"
        aria-label="Copy verify command"
      >
        {copied ? 'Copied' : 'Copy'}
      </button>
    </div>
  );
}

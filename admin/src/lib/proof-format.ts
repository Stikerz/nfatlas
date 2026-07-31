/**
 * Formatting helpers shared by the /proof page and its tests.
 *
 * Pure — no DOM, no React — so vitest runs them without jsdom.
 */

/**
 * Truncate a long hex string for display: first `chars` + ellipsis +
 * last `chars`. Returns the input unchanged if it's already short.
 */
export function shortHex(hex: string, chars = 12): string {
  if (hex.length <= chars * 2 + 1) return hex;
  return `${hex.slice(0, chars)}…${hex.slice(-chars)}`;
}

/**
 * Build the exact `verify_draw.py` CLI invocation for a given draw +
 * API base. Kept as a helper so a copy-paste path change lands in one
 * place.
 */
export function verifyCommandFor(drawId: string, apiBase: string): string {
  return `python backend/tools/verify_draw.py --proof-url ${apiBase}/api/v1/draws/${drawId}/proof`;
}

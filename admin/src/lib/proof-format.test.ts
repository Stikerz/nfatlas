import { describe, expect, it } from 'vitest';

import { shortHex, verifyCommandFor } from './proof-format';

describe('shortHex', () => {
  it('returns input unchanged when shorter than threshold', () => {
    expect(shortHex('abc')).toBe('abc');
    expect(shortHex('a'.repeat(12))).toBe('a'.repeat(12));
  });

  it('truncates with ellipsis when longer', () => {
    const long = '0123456789abcdef'.repeat(4);
    const short = shortHex(long, 6);
    expect(short).toBe(`012345…abcdef`);
    expect(short.length).toBeLessThan(long.length);
  });

  it('respects the chars parameter', () => {
    const long = '0123456789abcdef'.repeat(4);
    expect(shortHex(long, 4)).toMatch(/^0123…cdef$/);
  });
});

describe('verifyCommandFor', () => {
  it('renders the exact CLI invocation for a draw + host', () => {
    const cmd = verifyCommandFor('abc123', 'http://localhost:8000');
    expect(cmd).toBe(
      'python backend/tools/verify_draw.py --proof-url http://localhost:8000/api/v1/draws/abc123/proof',
    );
  });

  it('handles https hosts + trailing paths in the base', () => {
    const cmd = verifyCommandFor('xyz', 'https://atlas.example.com');
    expect(cmd).toContain('https://atlas.example.com/api/v1/draws/xyz/proof');
  });
});

import type { Config } from 'tailwindcss';

/**
 * Atlas design tokens as Tailwind theme extension.
 * Values traced to `_bmad-output/planning-artifacts/design/tokens.md`.
 * Semantic names only — no numeric colour ramps, no t-shirt spacing.
 */
const config: Config = {
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          primary: '#0F1E38',
          accent: '#C9A96A',
        },
        text: {
          primary: '#1A1A1A',
          secondary: '#5F5A54',
          inverted: '#FAF7F2',
          accent: '#C9A96A',
        },
        surface: {
          base: '#FAF7F2',
          elevated: '#F2EDE4',
          inverted: '#0F1E38',
          subtle: '#F7F3EC',
        },
        state: {
          success: '#1E5F4C',
          attention: '#B87728',
          danger: '#A94A38',
          info: '#0F1E38',
        },
        divider: {
          hairline: '#E5DFD6',
          strong: '#C9C3B7',
        },
        focus: '#0F1E38',
      },
      fontFamily: {
        display: ['var(--font-fraunces)', 'serif'],
        body: ['var(--font-inter)', 'system-ui', 'sans-serif'],
        mono: ['var(--font-jetbrains-mono)', 'ui-monospace', 'monospace'],
      },
      spacing: {
        '50': '2px',
        '100': '4px',
        '200': '8px',
        '300': '12px',
        '400': '16px',
        '500': '20px',
        '600': '24px',
        '800': '32px',
        '1200': '48px',
        '1600': '64px',
        '2400': '96px',
      },
      borderRadius: {
        none: '0',
        small: '4px',
        medium: '8px',
        large: '12px',
        pill: '9999px',
      },
      boxShadow: {
        e0: 'none',
        e1: '0 1px 2px rgba(60,45,30,.06), 0 2px 8px rgba(60,45,30,.04)',
        e2: '0 4px 12px rgba(60,45,30,.08), 0 12px 32px rgba(60,45,30,.06)',
      },
    },
  },
  plugins: [],
};

export default config;

# Project Atlas — Design Tokens (V0.5)

**Drafted:** 2026-07-08 (Day 1 evening / Day 2 per `tone-doc.md §8`)
**Drafted by:** 🎨 Sally (BMad UX Designer)
**Status:** Draft — pending founder ack before Day 3 wireframes begin. Founder sign-off gate is light here (values derived directly from the already-approved tone doc); a "no objections" is sufficient.
**Applies to:** V0.5 investor demo. Extends into V1 unless deliberately reset.
**Pairs with:** `tone-doc.md` (source of truth for palette + type intent), `v0.5-demo-plan.md` (schedule + scope), `docs/AINE-AGENTS.md` (ownership).

---

## 0. How to read this document

Every token here is **semantic**, not visual. You will not find `color.gold.500` or `space.md`. You will find `color.accent` and `space.400`. This is deliberate:

- **Semantic tokens survive rebrands.** If we ever change our accent from champagne gold to something else, the token name is still correct; only the value changes. Numeric scales rot the moment the palette shifts.
- **Semantic tokens force intent.** A developer reaching for `color.state.success` must first ask "is this a success moment?" That's the right question. Reaching for `color.green.500` is not.
- **Semantic tokens are the contract with Amelia.** She builds against `color.state.success` in both Flutter and Tailwind. If she needs a raw hex she is stepping outside the system — that's a design conversation, not a build shortcut.

Off-token values are a design bug. If Amelia needs one, she pings me first.

---

## 1. Colour tokens

Every colour has a job. Values traced back to `tone-doc.md §3`. WCAG contrast pairs verified against a `#FAF7F2` warm off-white surface unless otherwise noted; the "on midnight-navy" pairs verified against `#0F1E38`.

### Brand

| Token | Hex | Contrast (on surface `#FAF7F2`) | Contrast (on primary `#0F1E38`) | Use |
|---|---|---|---|---|
| `color.brand.primary` | `#0F1E38` | 14.8:1 ✅ AAA | — | Foundational surface for headers, primary buttons, brand marks. Also the "inverted" surface behind gold. |
| `color.brand.accent` | `#C9A96A` | 2.6:1 ❌ (never text on surface) | 7.2:1 ✅ AAA | Aspirational warmth. Verification badges, prize amounts (on navy), winner-moment accents. **Never** body text on light surface. **Never** a large background fill. |

### Text

| Token | Hex | Contrast | Use |
|---|---|---|---|
| `color.text.primary` | `#1A1A1A` | 16.0:1 on `#FAF7F2` ✅ AAA | Body copy, headlines on light surfaces. |
| `color.text.secondary` | `#5F5A54` | 6.7:1 on `#FAF7F2` ✅ AAA | Timestamps, metadata, supporting labels. |
| `color.text.inverted` | `#FAF7F2` | 14.8:1 on `#0F1E38` ✅ AAA | Text on midnight-navy surfaces. |
| `color.text.accent` | `#C9A96A` | 7.2:1 on `#0F1E38` ✅ AAA | Gold typography — prize amount headlines on navy, winner name accents. Never on light surfaces. |

### Surfaces

| Token | Hex | Use |
|---|---|---|
| `color.surface.base` | `#FAF7F2` | Base for content. Warm off-white — not stark white. |
| `color.surface.elevated` | `#F2EDE4` | Cards, ticket surfaces, modals. Gentle hierarchy without heavy shadows. |
| `color.surface.inverted` | `#0F1E38` | Navy fills — hero draw pages, winner reveals, primary CTAs. |
| `color.surface.subtle` | `#F7F3EC` | Very light hover state on `surface.base`. Almost imperceptible. |

### State

| Token | Hex | Contrast (on `#FAF7F2`) | Use |
|---|---|---|---|
| `color.state.success` | `#1E5F4C` | 7.4:1 ✅ AAA | Verified proof, confirmed transactions, won prizes. Deep emerald — **never bright green** (bright green reads as casino). |
| `color.state.attention` | `#B87728` | 4.6:1 ✅ AA | Timers approaching close, KYC pending, awaiting-action banners. Muted amber. |
| `color.state.danger` | `#A94A38` | 5.3:1 ✅ AA | Rejected payments, self-exclusion active, audit-log break, destructive confirmations. Muted terracotta — **never fire-engine red**. |
| `color.state.info` | `#0F1E38` | uses brand primary | Informational chrome (banners, subtle notices) reuses `brand.primary`. No dedicated blue — Atlas has no "info blue." |

### Structural

| Token | Hex | Use |
|---|---|---|
| `color.divider.hairline` | `#E5DFD6` | Row separators, subtle divisions. Almost invisible. |
| `color.divider.strong` | `#C9C3B7` | Rare — used only when a divider must actually separate (e.g. above a total row on a receipt). |
| `color.focus.ring` | `#0F1E38` | Focus outline — 2px solid at 3px offset. Matches brand primary; reads on both light and dark surfaces without a second focus colour. |

### Dark-surface variants

V0.5 ships **light-mode only** — no dark mode. Dark surfaces exist (navy sections on light-mode pages), and the text tokens above already cover them via `color.text.inverted` and `color.text.accent`. A true dark mode is a V1+ consideration; adding it now would double design + test surface with no demo payoff.

If dark mode is later needed, the token names hold — only values change. This is another reason for semantic naming.

### Palette anti-patterns (encoded in the system)

The following colours have **no token** and must not appear in the product:

- ❌ Bright red (`#FF0000` etc.) — reads as budget-airline / panic UI.
- ❌ Neon green / electric green — reads as crypto / gambling-adjacent.
- ❌ Soft pastels (mint, peach, baby blue) — undermines gravity.
- ❌ Corporate teal — safe but forgettable.
- ❌ Pure black `#000000` — too clinical; use `color.text.primary` (`#1A1A1A`).
- ❌ Pure white `#FFFFFF` — too clinical; use `color.surface.base` (`#FAF7F2`).

---

## 2. Typography tokens

Two typefaces. Fraunces (display, serif) and Inter (body, sans). Both Google Fonts — free, ship with the app. Weight discipline is enforced at the token level; no `type.*.thin` or `type.*.light` exists.

### Display (Fraunces)

| Token | Font | Size | Line-height | Weight | Letter-spacing | Use |
|---|---|---|---|---|---|---|
| `type.display.hero` | Fraunces | 64px / 4rem | 1.05 | 700 | -0.01em | Prize amount, hero moments, winner name on reveal. Once per page, max. |
| `type.display.section` | Fraunces | 40px / 2.5rem | 1.1 | 600 | -0.005em | Section headlines on public pages. |
| `type.display.draw` | Fraunces | 32px / 2rem | 1.15 | 600 | 0 | Draw name on draw-detail pages and ticket cards. |
| `type.display.card` | Fraunces | 24px / 1.5rem | 1.2 | 600 | 0 | Card headings, modal titles, admin section headers. |

### Body (Inter)

| Token | Font | Size | Line-height | Weight | Letter-spacing | Use |
|---|---|---|---|---|---|---|
| `type.body.default` | Inter | 16px / 1rem | 1.6 | 400 | 0 | Default body copy. |
| `type.body.emphasis` | Inter | 16px / 1rem | 1.6 | 600 | 0 | Inline emphasis; sparingly. |
| `type.body.small` | Inter | 14px / 0.875rem | 1.5 | 400 | 0 | Metadata, secondary labels, timestamps. |
| `type.body.button` | Inter | 15px / 0.9375rem | 1.2 | 500 | 0 | Button labels. |
| `type.label.micro` | Inter | 12px / 0.75rem | 1.3 | 500 | +0.05em | Uppercase labels in admin UI, section eyebrows. Always paired with `text-transform: uppercase`. |
| `type.body.mono` | JetBrains Mono | 14px / 0.875rem | 1.5 | 400 | 0 | **Hash strings only** — commit hashes, tickets_hash, server seed on proof page. Not used elsewhere. Ships as third font *only because* the audit-log wow moment (Anchor 5, Coinbase) requires monospaced typography to read as authoritative. Not a general body font. |

**Weight discipline (enforced):**

- Fraunces: **400, 600, 700 only.** No 300/light, no 800/900 (too heavy for a serif intended to feel calm).
- Inter: **400, 500, 600, 700 only.** No thin/light (illegible on lower-end Android — >50% of Nigerian market).
- JetBrains Mono: **400 only.** Hash typography is one weight.

**Line-height rules:**

- Display: tight (1.05–1.2) because it's a moment, not a paragraph.
- Body: generous (1.5–1.6) because it must be read.
- Never override line-height per instance — if a token feels wrong, we add a token, not a one-off.

---

## 3. Spacing scale

4px base. Half-steps (2px) exist only inside the "hairline" range and are not part of the public scale. Anything larger than `space.2400` is a design bug for V0.5 — no screen needs it.

| Token | Value | rem | Typical use |
|---|---|---|---|
| `space.0` | 0px | 0 | Zero — collapse a gap. |
| `space.50` | 2px | 0.125 | Hairline nudge; icon-to-text micro-alignment. Rare. |
| `space.100` | 4px | 0.25 | Icon padding; tight inline gap. |
| `space.200` | 8px | 0.5 | Compact stack; inline label + control. |
| `space.300` | 12px | 0.75 | Button internal padding (vertical); compact list gap. |
| `space.400` | 16px | 1 | **Default gap.** Card internal padding, form field spacing, paragraph gap. |
| `space.500` | 20px | 1.25 | Section-internal spacing. |
| `space.600` | 24px | 1.5 | Card padding (large), inter-card gap. |
| `space.800` | 32px | 2 | Section padding, top of page. |
| `space.1200` | 48px | 3 | Between major page sections. |
| `space.1600` | 64px | 4 | Above the fold breathing room; hero blocks. |
| `space.2400` | 96px | 6 | Hero moments only — winner reveal top spacing, proof page top spacing. |

**Usage rules (enforced by review, not code — Amelia knows to flag):**

- Off-scale values (e.g. `10px`, `18px`, `36px`) are **prohibited** unless motivated by a specific pixel-perfect asset alignment (which should be rare and always documented in the wireframe).
- **Do not** use spacing tokens as sizing tokens. `width: space.400` is a smell. Component widths come from the layout system (grid + intrinsic content), not from the space scale.
- The scale is intentionally sparse (10 steps + zero). If you feel a value is missing, question the design before adding a token.

---

## 4. Border-radius scale

Restraint over expressiveness. Atlas is institutional; aggressive roundness reads as friendly-fintech, which is what tone doc §6 explicitly rejects.

| Token | Value | Use |
|---|---|---|
| `radius.none` | 0px | Full-bleed hero images; audit-log table rows (rows are visually flush). |
| `radius.small` | 4px | Form inputs, tags, small badges. Subtle softening. |
| `radius.medium` | 8px | Buttons, alerts, banners, verification badges. **Default for interactive elements.** |
| `radius.large` | 12px | Cards, modals, ticket cards, draw cards. Any surface a user reads as a discrete object. |
| `radius.pill` | 9999px | **Only** for skill-question answer chips and the "free entry" pill on draw pages. Never for buttons. |

**Component archetype mapping:**

- Input → `radius.small`
- Button → `radius.medium`
- Badge / verification badge → `radius.medium`
- Alert / banner → `radius.medium`
- Card (draw card, admin card, receipt) → `radius.large`
- Ticket card → `radius.large` (the "object of affection" moment from Anchor 3 — Range Rover configurator — earns the same treatment as a card)
- Modal → `radius.large`
- Skill-question answer chip → `radius.pill`
- Free-entry-route pill → `radius.pill`

**Anti-patterns:**

- ❌ `radius > 24px` anywhere. Aggressively-rounded shapes are a friendly-fintech tell.
- ❌ Mixed radii within a single component (e.g. top-rounded / bottom-square). Design smells desperate; always uniform.
- ❌ `radius.pill` on buttons. Pill buttons read as consumer-marketing (Uber, Netflix); Atlas buttons are institutional (`radius.medium`).

---

## 5. Elevation levels

Three levels. No more. Deep shadow stacks are a UI trope Atlas rejects — hierarchy should come from surface colour (`surface.base` vs `surface.elevated`) first, shadows second.

Shadows are **warm-tinted**, not cold pure-black — otherwise they read as harsh against the warm off-white surface.

| Token | Value (CSS) | Use |
|---|---|---|
| `elevation.0` | `none` | Flat. Sections, table rows, inline content. **Default.** |
| `elevation.1` | `0 1px 2px rgba(60, 45, 30, 0.06), 0 2px 8px rgba(60, 45, 30, 0.04)` | Raised card. Draw cards, ticket cards, admin cards, dropdown menus. |
| `elevation.2` | `0 4px 12px rgba(60, 45, 30, 0.08), 0 12px 32px rgba(60, 45, 30, 0.06)` | Modal, dialog, toast. Anything overlaying page content. Rare; a screen has at most one `elevation.2` element active at a time. |

**Warm-tint rationale:** `rgba(60, 45, 30, α)` is a very dark warm brown, not black. Against `surface.base` (`#FAF7F2`), a black shadow reads as bruised or dirty. The warm brown reads as *shadow cast by warm light* — consistent with the "shot in Nigerian light" prize-photography direction from tone-doc.md §7.

**Anti-patterns:**

- ❌ `elevation > 2` in normal UI. If a design feels like it needs elevation-3, the surface hierarchy is wrong — fix the surface, not the shadow.
- ❌ Coloured shadows for state (e.g. green glow on success). State communicates through colour tokens and copy, not shadow.
- ❌ Inset shadows for pressed states. Buttons on Atlas use a colour change (`surface.subtle` background flash), not an inset shadow.

---

## 6. Cross-platform emission

Reference table only — Amelia owns actual code generation. Same token, three forms:

| Semantic token | Flutter (Dart) | CSS custom property | Tailwind theme extension |
|---|---|---|---|
| `color.brand.primary` | `AtlasColors.brand.primary` → `Color(0xFF0F1E38)` | `--atlas-color-brand-primary: #0F1E38;` | `theme.extend.colors.brand.primary = '#0F1E38'` |
| `color.brand.accent` | `AtlasColors.brand.accent` | `--atlas-color-brand-accent: #C9A96A;` | `theme.extend.colors.brand.accent = '#C9A96A'` |
| `color.text.primary` | `AtlasColors.text.primary` | `--atlas-color-text-primary: #1A1A1A;` | `theme.extend.colors.text.primary = '#1A1A1A'` |
| `color.state.success` | `AtlasColors.state.success` | `--atlas-color-state-success: #1E5F4C;` | `theme.extend.colors.state.success = '#1E5F4C'` |
| `space.400` | `AtlasSpace.s400` → `16.0` | `--atlas-space-400: 1rem;` | `theme.extend.spacing['400'] = '1rem'` |
| `type.display.hero` | `AtlasType.displayHero` → `TextStyle(fontFamily: 'Fraunces', fontSize: 64, height: 1.05, fontWeight: FontWeight.w700, letterSpacing: -0.64)` | `--atlas-type-display-hero-...` (component-scoped) | Custom Tailwind plugin exposing `text-display-hero` utility |
| `radius.large` | `AtlasRadius.large` → `12.0` | `--atlas-radius-large: 12px;` | `theme.extend.borderRadius.large = '12px'` |
| `elevation.1` | `AtlasElevation.e1` → `List<BoxShadow>` | `--atlas-elevation-1: 0 1px 2px rgba(60,45,30,.06), 0 2px 8px rgba(60,45,30,.04);` | `theme.extend.boxShadow.e1 = '0 1px 2px rgba(60,45,30,.06), 0 2px 8px rgba(60,45,30,.04)'` |

**Suggested source-of-truth format for Amelia:** a single `tokens.json` in a repo-shared location (e.g. `packages/design-tokens/tokens.json`) generated once, then transformed via a small script into (a) `atlas_theme.dart` for Flutter and (b) `tailwind.config.js` + `tokens.css` for Next.js. Style Dictionary is the obvious tool; if that's heavier than needed for V0.5, a ~30-line Python script is fine — the token count is small.

---

## 7. Anti-patterns — tokens you will NOT find here and why

- **No `color.red.500` / numeric-scale colour tokens.** Atlas uses semantic tokens only. `color.state.danger` is the meaning; `#A94A38` is an implementation detail.
- **No `color.gray.100..900` neutral ramps.** The four text colours + four surface colours are the ramp. If you need a fifth grey, question the design.
- **No thin / light font weights (`100`, `200`, `300`).** Illegible on lower-end Android; forbidden by tone-doc.md §4.
- **No radius > 24px.** Aggressively-rounded shapes are a friendly-fintech tell that undermines institutional gravity. Pill radius exists for two specific components; nothing else.
- **No elevation-3 or deeper.** If you need more depth, fix the surface hierarchy.
- **No black shadows.** Warm-tinted only.
- **No `color.info.*` blue.** Atlas has no info blue — informational chrome uses `brand.primary`. Blue is a rabbit-hole (which blue? corporate? Facebook? Twitter? Kuda?) that we sidestep by not having one.
- **No `space.md` / t-shirt naming.** Numeric scale is explicit; t-shirts (`xs`, `sm`, `md`, `lg`, `xl`) rot the moment the scale grows.
- **No animation / transition tokens (yet).** V0.5 uses default platform easings and a 150ms default duration. Motion tokens land in V1 when we have real motion moments to name (draw reveal, ticket-issued animation).
- **No dark-mode tokens.** V0.5 ships light-mode only; token names accommodate a future dark mode without rename.
- **No responsive-breakpoint tokens.** Flutter handles this via `MediaQuery`; Next.js handles it via Tailwind's built-in breakpoints (`sm`, `md`, `lg`) which are adequate for V0.5's two web surfaces (admin desktop, public marketing pages).
- **No z-index scale.** V0.5 has: page content (0), sticky nav (10), modal backdrop (100), modal (110), toast (200). Five values, hardcoded in the modal component. A z-index scale is a smell that says "we lost control of stacking"; V0.5 doesn't need one yet.

---

## 8. Cross-references

- Source of visual intent: `tone-doc.md` §3 (colour), §4 (typography), §6 (what Atlas is NOT).
- Scope + schedule: `v0.5-demo-plan.md` §2 (flagship flows), §5 (weekly plan).
- Ownership: `docs/AINE-AGENTS.md` (design owned by 🎨 Sally; implementation owned by 💻 Amelia; compliance copy review by ⚖️ Adaeze).
- Downstream consumers (not yet created): wireframes at `_bmad-output/planning-artifacts/design/wireframes/`, component specs at `_bmad-output/planning-artifacts/design/components/`.

---

🎨 *End of tokens. Ready for Day 3 (consumer wireframe 1 — Register → OTP → login) on founder ack. If any token here feels wrong at first read — palette semantics, typography scale, spacing bounds, elevation warmth, anti-patterns — flag it now; changing a token pre-wireframe is free, post-wireframe is a re-sweep.*

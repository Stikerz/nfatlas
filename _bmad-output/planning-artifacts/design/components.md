# Project Atlas — V0.5 Mini Design System

**Drafted:** 2026-07-08 (Day 13 per `tone-doc.md §8`)
**Drafted by:** 🎨 Sally (BMad UX Designer)
**Status:** Draft — pending founder + 💻 Amelia review at Week 2 exit (Day 14). This artefact is the handoff to Amelia for Week 3 build.
**Applies to:** V0.5 investor demo. Every wireframe under `_bmad-output/planning-artifacts/design/wireframes/01..15` composes from the primitives specified here.
**Pairs with:** `tokens.md`, `tone-doc.md`, all wireframes.

---

## 0. What this document is (and isn't)

**Is:** a specification of the 15 primitive components the V0.5 wireframes depend on. Each entry has purpose, prop shape, variants, states, tokens consumed, accessibility contract, and a usage index pointing at every wireframe that composes it. Amelia builds these once; every wireframe that composes them inherits the contract automatically.

**Isn't:** a catalog of every component name that appears in a wireframe. Many wireframes call out one-off compositions (`TicketArtefact` on wf-05, `VerdictCard` on wf-14, `CommitmentReceiptCard` on wf-09, etc.) — those are *combinations of the 15 primitives dressed for a specific screen*. They are documented in their host wireframes; they are not primitives in the system, they are compositions. Section §17 catalogs the compositions and points at where they're specified.

**Isn't:** a Figma library. V0.5 wireframes are text-first specs by design (per tone-doc.md §8 deliverables format). Amelia builds primitives from this spec directly in Flutter and Next.js; a shared Figma library becomes a V1 concern when the design surface grows past two people.

**Isn't:** the design tokens themselves. Tokens live in `tokens.md` and are consumed by every component here. This document says *which tokens each component uses*; the tokens themselves are canonical over there.

---

## 1. Design principles (that every component honours)

Every component below is built to these principles. Deviation requires a design amendment, not an implementation shortcut.

1. **Semantic tokens only.** Components consume `color.brand.primary`, not `#0F1E38`. Consume `space.400`, not `16px`. If a component wants a value the token set doesn't provide, that's a design conversation.
2. **State is legible without colour.** Colour is one signal; icon shape and copy are always additional signals. Colour-independence per WCAG.
3. **Touch targets ≥ 44×44pt.** Every interactive element.
4. **Focus visible.** Every focusable element has a visible focus ring using `color.focus.ring`. No `outline: none` without a replacement.
5. **Reduce-motion respected.** Every animation has a reduce-motion variant that removes motion and preserves the semantic transition.
6. **Screen-reader complete.** Every meaningful element has an accessible name; state changes announce via `aria-live` where appropriate.
7. **Cross-platform parity.** Flutter and Next.js implementations produce the same visual + interaction contract. If one platform can't honour a spec fully, that's a design amendment for both, not a silent divergence.
8. **No decorative-only elements.** Every visible element serves a purpose the reader can name.
9. **Composition over configuration.** If a component needs more than ~6 props, it's probably two components.
10. **The design system is a floor, not a ceiling.** Wireframes compose primitives into specific screens. New primitives are added when a pattern truly recurs (≥3 uses); one-off compositions stay in the wireframe that defines them.

---

## 2. Component index (the 15 primitives)

| # | Component | §  | Primary tokens | Wireframes |
|---|---|---|---|---|
| 1 | Button | §3 | brand.primary, radius.medium, type.body.button | 01, 04, 06, 07, 08, 09, 10, 11, 12, 13, 14, 15 |
| 2 | Input | §4 | radius.small, hairline, label.micro, body.default | 01, 04, 07, 08, 09, 10 |
| 3 | Ticket card | §5 | surface.elevated, radius.large, elevation.1, mono | 05 |
| 4 | Draw card | §6 | surface.elevated, radius.large, elevation.1 | 02, 09, 15 |
| 5 | Timer | §7 | body.default, state.attention (near-close) | 02, 06 |
| 6 | Table row | §8 | body.default, hairline dividers | 09 (draws), 13 (audit) |
| 7 | Banner | §9 | state.* @ 12% + solid 4pt left border | 01, 04, 06, 08, 13 |
| 8 | Skill-question card (AnswerChip) | §10 | radius.pill, surface.base, hairline | 04 |
| 9 | Audit-log row | §11 | body.default, mono, state indicators | 13 |
| 10 | Verification badge | §12 | brand.accent gold, state.success emerald | 02, 05, 06, 07, 14 |
| 11 | Empty state | §13 | surface.elevated illustration slot, secondary text | 02, 05, 13 |
| 12 | Error state | §14 | state.danger, retry-CTA | 02, 04, 05, 06, 08, 13 |
| 13 | Modal | §15 | elevation.2, radius.large, focus trap | 04, 08, 09, 11, 12, 15 |
| 14 | Toast | §16 | surface.inverted, body.small, brand.accent tint | 02, 03, 04, 05, 09, 10, 11, 12, 13, 15 |
| 15 | Nav bar | §17 | surface.base + hairline, label.micro | 02 (bottom), 05, 08 (sidebar), 13 |

Compositions built from these primitives: catalog in §18.

---

## 3. Button

### 3.1 Purpose

The default interactive commitment element. Every explicit user action ("Enter", "Pay", "Publish", "Submit claim", "Sign in") is a button. If a control is doing something else (opening a page, navigating, revealing info), it's probably an `InlineLink`, not a button.

### 3.2 Props

```
{
  label:      string           // required
  variant:    "primary" | "secondary" | "danger"    // default "primary"
  size:       "medium" | "large"                     // default "medium" (48pt); "large" = 52pt
  width:      "auto" | "full"                        // default "auto"; "full" = 100% container
  disabled:   boolean                                // default false
  loading:    boolean                                // default false; replaces label with spinner + optional loadingLabel
  loadingLabel: string                               // optional (e.g. "Signing in…"); if absent, spinner-only
  leadingIcon: Icon                                  // optional
  trailingIcon: Icon                                 // optional (e.g. → arrow on Next)
  onPress:    () => void                             // required
  // "attention hint" is a bounded exception per §3.5 wf-09 §5.4 pattern
  attentionHint: boolean                             // default false; adds subtle attention-tint background
}
```

### 3.3 Variants

**Primary** — `color.brand.primary` fill, `color.text.inverted` text, `radius.medium`. The default. Every screen has at most one visible primary button at a time (excluding sticky footers).

**Secondary** — transparent fill, `color.brand.primary` 1px border, `color.brand.primary` text, `radius.medium`. Used for "back" actions in multi-step flows, or when a primary is already elsewhere on the screen.

**Danger** — transparent fill, `color.state.danger` text, no border. Used for destructive inline actions ("Cancel this entry", "Remove ticket"). Rare.

### 3.4 States

| State | Visual |
|---|---|
| Default | As specified per variant |
| Hover (web) | Slight brightness adjustment; no shape change |
| Pressed | 100ms flash of `surface.subtle` overlay on primary; no shape change |
| Focused | 2pt `color.focus.ring` outline at 3pt offset |
| Disabled | Primary: `surface.elevated` fill + `text.secondary` text (5.6:1, still legible per WCAG). Secondary: `text.secondary` border + text. Danger: `text.secondary` text. Never invisible; disabled ≠ hidden |
| Loading | Label replaced with inline spinner (16pt); optional `loadingLabel` (*"Signing in…"* / *"Publishing…"*); button remains rendered at same width |
| Attention hint (bounded exception) | Primary variant only: 12% `color.state.attention` overlay on the fill. Used exclusively on irreversible-action buttons per wf-09 §5.4. |

### 3.5 Tokens

- `color.brand.primary` — primary fill
- `color.text.inverted` — primary text
- `color.state.danger` — danger text
- `color.surface.elevated` — disabled primary fill
- `color.text.secondary` — disabled text
- `color.focus.ring` — focus outline
- `color.state.attention` — attention hint (bounded)
- `radius.medium` — border radius
- `type.body.button` — label typography (Inter 15pt / 500)
- `space.400` (16pt) — horizontal padding (medium size)
- `space.600` (24pt) — horizontal padding (large size)

### 3.6 Accessibility

- Must be a native `<button>` (web) / `ElevatedButton` or `TextButton` (Flutter).
- Focus visible per §1 principle 4.
- Disabled state uses `aria-disabled="true"` (not the `disabled` HTML attribute) so it remains in tab order and announces "disabled" — allows focus-attempt to trigger helper announcements.
- Loading state announces `aria-busy="true"`.
- `aria-describedby` for buttons with helper text near them (e.g. Publish button on wf-09 §5.3 with the "Publish is guarded by a confirmation modal" note).
- Icons carry `aria-hidden="true"` — the label carries the accessible name.

### 3.7 Usage index

Every wireframe uses buttons. The attention-hint variant is used at wf-09 §5.3 (Publish draw), wf-11 §2.1 (Close draw), wf-12 §2.1 (Start ceremony).

---

## 4. Input

### 4.1 Purpose

Every field the user types into. One primitive with variants for text, password, number, phone (with dial-code), date, and OTP (6-digit segmented).

### 4.2 Props

```
{
  variant:    "text" | "password" | "number" | "phone" | "date" | "otp"
  label:      string                        // required (label.micro uppercase)
  value:      string
  placeholder: string
  helper:     string                        // subtle body.small under field
  required:   boolean                        // default false; adds ▪ gold prefix on label + aria-required
  disabled:   boolean
  error:      string                        // if present, field enters error state; text shown below in state.danger
  onChange:   (value) => void
  autofillHint: string                       // maps to autocomplete attribute (web) or Flutter AutofillHints
  inputMode:  "text" | "numeric" | "email" | "tel"    // per variant default; overridable
  onBlur:     () => void
}
```

Variant-specific props:
- **password:** `showToggle` (default true) — the eye/eye-slash toggle.
- **phone:** `dialCode` (default `+234` for V0.5, fixed chip).
- **date:** `min` / `max` boundaries.
- **otp:** `length` (default 6).

### 4.3 Variants + variant-specific behaviour

- **text** — the default. Autocorrect off unless specified.
- **password** — obscures text; show-toggle auto-reverts to obscured after 5s (per wf-01 §4.3).
- **number** — numeric keyboard; formatting on blur (thousands separators for money per wf-09 §3.3).
- **phone** — fixed dial-code chip + numeric input (V0.5); country picker replaces chip in V1.
- **date** — native date picker (Flutter `showDatePicker`; web `<input type="date">`).
- **otp** — 6-digit segmented boxes; auto-advance per digit; paste populates all boxes; iOS `.oneTimeCode`; Android SMS Retriever.

### 4.4 States

| State | Visual |
|---|---|
| Empty | Placeholder text in `color.text.secondary` |
| Focused | 2pt `color.focus.ring` outline at 1pt offset |
| Filled | Value in `color.text.primary`; label lifts (Flutter default) or stays above (web default) |
| Error | 1pt border in `color.state.danger`; error text below in `color.state.danger` body.small |
| Disabled | Fill `color.surface.elevated`; text `color.text.secondary`; cursor not-allowed |
| Read-only (verified) | Field non-editable with a trailing `✓ verified` chip (used for pre-filled DOB per wf-01 amendment, phone + email in wf-07 §4.1) |

### 4.5 Tokens

- `radius.small` (4pt) — border radius
- `color.divider.hairline` — default border
- `color.state.danger` — error border + text
- `color.surface.elevated` — disabled fill
- `color.text.primary` / `.secondary` — value + placeholder
- `type.label.micro` (12pt uppercase +0.05em) — label
- `type.body.default` (16pt) — value
- `type.body.small` (14pt) — helper + error text
- Height: `48pt` (all variants except OTP boxes which are 48pt square)
- `color.focus.ring` — focus outline

### 4.6 Accessibility

- `<label for="...">` association required (never placeholder-as-label).
- `aria-required="true"` for required.
- `aria-invalid="true"` when in error state.
- `aria-describedby` linking to helper text and error text.
- `aria-live="polite"` on error text container.
- OTP: input group announced as *"one-time code, 6 digits"*; digit-entered progress announced.
- Autofill hints per variant (`autocomplete` on web; `AutofillHints.*` on Flutter).
- Show/hide password: `<button>` with `aria-label="Show password"` / `"Hide password"`.

### 4.7 Usage index

Text: 01, 04, 07, 08, 09, 10.
Password: 01, 08.
Number: 09, 10.
Phone: 01, 10.
Date: 01, 07 (read-only after amendment), 09, 10.
OTP: 01.

---

## 5. Ticket card

### 5.1 Purpose

The compact list-view representation of a user's ticket, used on the My Tickets list (wf-05 §2). Not to be confused with `TicketArtefact` (the enlarged hero variant in wf-05 §3, §18.1 in this doc) — the ticket card is the list-row primitive; the artefact is a composition dressed for the detail page.

### 5.2 Props

```
{
  ticketNumber:   string     // rendered mono
  drawTitle:      string     // e.g. "₦2,000,000 in cash"
  purchasedAt:    ISO-8601
  entrySource:    "paid" | "free_route"
  outcome:        "active" | "awaiting_reveal" | "won" | "not_won"
  onPress:        () => void  // opens ticket detail (wf-05 §3)
}
```

### 5.3 Variants

Governed by `outcome`:

- **active** — default treatment. Trailing `✓ Paid entry` (or `✓ Free-route entry`) chip.
- **awaiting_reveal** — subtle *"Awaiting draw"* chip corner-placed.
- **won** — **special treatment**: full-width `color.brand.primary` top strip 24pt tall with gold "Winning ticket" label; ticket number in `color.text.accent` (gold — the one place gold typography appears on a light surface per tokens.md); emerald `✓ Winner` chip; bottom "See how to claim your prize" primary CTA.
- **not_won** — soft `surface.subtle` tint; `Not this time.` line at bottom; no CTA.

### 5.4 Layout (compact list variant)

120pt tall, full-width, `radius.large`, `elevation.1`, `surface.elevated`, hairline border, 16pt padding. Composition:
- `▪ Atlas — Ticket` sub-brand line (label.micro uppercase gold).
- Ticket number (mono, 32pt).
- Hairline divider (subtle).
- Draw title (body.default primary).
- Purchased-at timestamp (body.small secondary).
- Entry-source chip (body.small state.success).

### 5.5 Tokens

- `radius.large` (12pt)
- `elevation.1`
- `color.surface.elevated`
- `color.divider.hairline`
- `type.body.mono` (JetBrains Mono 14pt base; overridden to 32pt for the ticket number)
- `color.text.accent` — winning ticket number gold (bounded exception per tokens.md)
- `color.brand.primary` — winning strip fill
- `color.state.success` — Winner chip
- `color.state.attention` — awaiting-reveal chip

### 5.6 Accessibility

- Composite tap target: whole card is `Semantics(button:true)` (Flutter) / `role="link"` (web).
- Accessible name: *"Ticket zero four eight two nine. Two million naira in cash draw. Purchased 8 July, 14:23. Paid entry. Tap to view details."*
- Winning variant announces *"Winning ticket"* first: *"Winning ticket. Ticket zero four eight two nine…"*
- Ticket number read digit-by-digit (not "four thousand eight hundred twenty nine").
- Trailing chip announced as *"Winner"* / *"Paid entry"* / etc.

### 5.7 Usage index

Wireframe 05 §2 (list) — every ticket the user holds. Compositions of the same base component with the "won" variant dress up as `TicketArtefact` on wf-05 §3.

---

## 6. Draw card

### 6.1 Purpose

The consumer surface's primary representation of a single draw. Used on the home surface (wf-02 §2), on the admin review-before-publish preview (wf-09 §5.3 — renders the *same* component so operator sees exactly what consumers will see), and on trust-story pages when referencing an active draw (wf-15 Part B).

### 6.2 Props

```
{
  drawTitle:      string      // e.g. "₦2,000,000"
  drawUnit:       string      // e.g. "in cash"
  prizeImage:     URL
  prizeImageAlt:  string
  closeAt:        ISO-8601
  entryCounts:    { paid: number, free: number }
  entryPrice:     integer_kobo
  status:         "open" | "closing_soon" | "closed" | "awaiting_reveal" | "revealed"
  ctaLabel:       string     // "View draw" (open), "See the proof" (revealed), etc
  onPressCta:     () => void
  onPressCard:    () => void
  winner:         { name?: string, city?: string }  // present only if status "revealed"
}
```

### 6.3 Variants (by status)

- **open** — as drawn in wf-02 §2.
- **closing_soon** — timer switches to `color.state.attention` (see §7).
- **closed** — section eyebrow changes to *"This draw has closed"*; CTA remains *"View draw"* (opens post-close detail).
- **awaiting_reveal** — CTA remains *"View draw"*; timer replaced by *"Awaiting reveal — announced {reveal_time}"*.
- **revealed** — prize amount replaced by winner-name treatment (respecting consent — anonymous fallback: *"₦2,000,000 won by Winner — {city}"*); CTA: *"See the proof"*.

### 6.4 Layout

Card, `radius.large`, `elevation.1`, `surface.elevated`. Prize photograph slot (4:3, radius-large top, square bottom — image sits flush inside card top edge). Prize amount in `type.display.hero` (64pt Fraunces). Unit line body.default secondary. Hairline. Close-time line body.default primary. Entry-count line body.small secondary. Full-width secondary-variant CTA at the bottom.

### 6.5 Tokens

- Same as ticket-card core (radius.large / elevation.1 / surface.elevated).
- `type.display.hero` for the prize amount.
- `color.text.accent` — winner name (revealed variant, gold on elevated surface, bounded exception).

### 6.6 Accessibility

- Composite tap target with fallback to explicit CTA.
- Composed accessible name summarises: *"This week's draw. Two million naira in cash. Closes 8pm Saturday. 1,247 entries, 87 via the free route. View draw."*
- Prize image alt-text required.
- Timer state changes announced via `aria-live="polite"` on the timer inside the card (per §7).

### 6.7 Usage index

- wf-02 §2 (consumer home)
- wf-09 §5.3 (admin review preview — same component, live-rendered)
- wf-15 Part B (trust-story page when active draw exists)

---

## 7. Timer

### 7.1 Purpose

A relative-countdown line paired with an absolute-time line. Renders across the product wherever a draw's close-time or reveal-time is shown alongside a live countdown. Never used alone — always paired with the absolute time above.

### 7.2 Props

```
{
  targetTime:     ISO-8601
  format:         "long" | "short"    // "long" = "3 days, 8 hours"; "short" = "3d 8h"
  updateEvery:    "minute" | "second"  // default "minute" (visual noise otherwise)
  attentionThresholdMinutes: number    // default 240 (4 hours); below this, colour shifts to state.attention
}
```

### 7.3 Variants

Governed internally by remaining time:
- **Default** (>attentionThreshold) — `color.text.secondary`.
- **Approaching close** (<attentionThreshold) — `color.state.attention` (muted amber).
- **Zero / past** — replaced by *"Closed"* or handed to the container's post-close copy.

### 7.4 States

Auto-updating text; no user-facing state beyond the variants above.

### 7.5 Tokens

- `type.body.default` (16pt) — text
- `type.body.small` — when embedded as sub-line
- `color.text.secondary` — default
- `color.state.attention` — approaching-close

### 7.6 Accessibility

- Updates announced only at *significant* milestones — the transition from default → attention state, and on hitting 0. Not every minute (spam).
- `aria-live="polite"` on the state-change announcements only, not on every tick.
- Never colour-only for state signalling — copy carries the information (*"Closes in 3 hours 24 minutes"*).

### 7.7 Usage index

- wf-02 §3.1 (draw detail close-time area)
- wf-06 §3 (reveal page timing context)

---

## 8. Table row

### 8.1 Purpose

A row in a data table on admin surfaces. Two flavours: draws-list rows (wf-09 §2 entry point) and audit-log rows (wf-13 §2.1 — see also §11 for the specialised audit row). This entry is the primitive; the audit row is a specialisation.

### 8.2 Props

```
{
  cells:      Cell[]                      // ordered per table column
  onPress:    () => void                   // opens detail
  highlight:  "none" | "attention" | "danger"    // for rows requiring visual attention
}
```

### 8.3 Layout

Full-width, 48pt-tall row. Hairline divider between rows. Left/right padding 16pt. First-cell often carries a status dot (per column spec). Trailing cell often carries an action or chevron.

### 8.4 States

- **Default** — as drawn.
- **Hover (web)** — subtle `color.surface.subtle` fill.
- **Focused** — 2pt focus ring around row.
- **Highlighted (attention)** — 4pt left border in `color.state.attention`, subtle amber tint.
- **Highlighted (danger)** — 4pt left border in `color.state.danger` (used on audit-log rows inside a broken chain range per wf-13 §2.3).

### 8.5 Tokens

- `color.divider.hairline` — row separators
- `type.body.default` — cell text default
- `type.body.mono` — for hash / ID cells
- `space.400` — cell padding

### 8.6 Accessibility

- Uses proper `<table>` / `<thead>` / `<tbody>` semantics on web.
- Column headers `<th scope="col">`.
- Rows focusable (`tabindex="0"`); Enter opens detail.
- Sortable columns not offered in V0.5 (default sort only).

### 8.7 Usage index

- wf-09 §2 (draws list entry)
- wf-13 §2.1 (audit log — see §11 for the specialised row)

---

## 9. Banner

### 9.1 Purpose

A top-of-content region notification. Used for errors ("We couldn't send the code"), attention states ("Chain integrity broken"), and success confirmations (used sparingly — most successes get a Toast §14 rather than a banner).

### 9.2 Props

```
{
  variant:    "info" | "success" | "attention" | "danger"
  headline:   string     // optional; short
  body:       string     // required
  dismissible: boolean    // default true
  onDismiss:  () => void
  actions:    Action[]    // optional inline actions
}
```

### 9.3 Variants

Each variant uses its state colour at 12% opacity as background, plus a solid 4pt left border in the state colour, plus the state colour for text.

- **info** — `color.brand.primary` accents (rare on consumer surfaces; used on admin for informational banners).
- **success** — `color.state.success` accents.
- **attention** — `color.state.attention` accents.
- **danger** — `color.state.danger` accents.

### 9.4 States

- Default (as drawn).
- Dismissed — animates out (fade + slight collapse). Reduce-motion: instant.

### 9.5 Tokens

- `color.state.*` — all four states
- `radius.medium` (8pt) — border radius
- `type.body.default` — body
- `type.body.emphasis` — headline if present
- `space.400` — padding

### 9.6 Accessibility

- **Danger + attention banners:** `role="alert"` — highest-priority announcement.
- **Info + success:** `role="status"` — polite announcement.
- Dismissible banners have `<button>` for dismissal with `aria-label="Dismiss"`.
- If the banner replaces a specific UI element's error state (e.g. login-form banner above the card), it stays adjacent to that element for focus-relationship clarity.

### 9.7 Usage index

- Error banners on: wf-01, wf-04, wf-05, wf-06, wf-08, wf-13.
- Chain-BROKEN banner: wf-13 §2.3 (specialised — full-page-width, non-dismissible).

---

## 10. Skill-question card (AnswerChip)

### 10.1 Purpose

The individual answer-option chip on the skill-question screen (wf-04 §2). This is the *chip*, not the whole question-and-4-answers layout — the layout composes 4 chips.

### 10.2 Props

```
{
  letter:     "A" | "B" | "C" | "D"
  answer:     string
  state:      "default" | "selected_correct" | "selected_incorrect"
  onPress:    () => void
}
```

### 10.3 Layout

Full-width, 56pt tall, `radius.pill` (this is one of two places pill radius is used per tokens.md), 12pt gap between chips. Composition:
- Letter label on the left (Fraunces 20pt).
- Answer text (Inter body.default primary).
- On selected states, a trailing check or ✕ icon fades in.

### 10.4 States

- **default** — `surface.base` fill, hairline border, `color.text.primary` text.
- **selected_correct** — `color.state.success` fill, `color.text.inverted` text, trailing check icon. Held for 400ms then screen navigates.
- **selected_incorrect** — `color.state.danger` fill for 400ms then returns to default; other chips shake gently (per wf-04 §2.3).
- **disabled** — inline spinner replaces the letter briefly during server validation.

### 10.5 Tokens

- `radius.pill`
- `color.state.success` / `color.state.danger` for state fills
- `color.text.inverted` on filled states
- Fraunces 20pt for letter; Inter body.default for answer

### 10.6 Accessibility

- Each chip: `role="radio"` grouped inside `role="radiogroup"` labelled by the question.
- First chip focused on screen mount; keyboard arrow keys move focus between radios (standard ARIA radio pattern).
- Selection announcement via `aria-live="assertive"` on the correct/incorrect state.
- Colour-independence: correct/incorrect always accompanied by icon (check / ✕) or text.

### 10.7 Usage index

- wf-04 §2 (skill question — 4 chips per question).

---

## 11. Audit-log row

### 11.1 Purpose

The specialised table row in the audit-log surface (wf-13 §2.1). Distinct enough from a generic table row (§8) to be a first-class primitive: it carries the chain state per row and a compact hash preview cell.

### 11.2 Props

```
{
  seq:        integer
  occurredAt: ISO-8601
  eventName:  string           // kebab-case, mono
  subjectType: string
  subjectId:  string
  actor:      { type: "system" | "operator" | "user", name?: string }
  chainState: "intact" | "broken"     // per-row chain check result
  onPress:    () => void
}
```

### 11.3 Layout

6-column table row: `#` (seq, mono) / `Time (WAT)` (body.default) / `Event` (mono) / `Subject` (body.default with mono ID suffix) / `Actor` (body.default with system italic for automated actors) / `Chain` (tick or warning icon).

### 11.4 States

- **Chain intact** — trailing `✓` in `color.state.success`.
- **Chain broken** — trailing `⚠` in `color.state.danger`, plus row-level `highlight="danger"` (per §8.4).

### 11.5 Tokens

- Same as table row §8.5.
- `type.body.mono` — seq + event + subject-ID cells.

### 11.6 Accessibility

- Chain-state icon is never colour-only (icon shape carries meaning).
- Broken rows announced first when the surface loads (per wf-13 §2.3 chain-broken behaviour).
- Actor cell distinguishes `system` vs `operator` audibly (*"system"* / *"operator Adaobi Ibe"*).

### 11.7 Usage index

- wf-13 §2.1 (audit log index).
- wf-14 §3.8 (public proof — a subset of these rows shown in the audit-trail excerpt, but with the actor column omitted).

---

## 12. Verification badge

### 12.1 Purpose

A small visual mark asserting that a piece of content has been verified or a state has been reached. Not a decorative element — appears specifically where the trust story is being redeemed.

### 12.2 Props

```
{
  variant:    "verified" | "winner" | "self_excluded" | "kyc_verified"
  size:       "small" | "medium" | "large"    // 16 / 24 / 48pt
  labelInline: string   // optional; renders text to the right of the badge
}
```

### 12.3 Variants

- **verified** — gold check-in-circle. Used on the proof page (wf-14 VerdictCard), on the reveal page (wf-06 §3), on the commit receipts (wf-09/11/12 §7).
- **winner** — emerald check with *"Winner"* label. Used on the winning ticket (wf-05 §2.5, wf-05 §3.2, wf-06 §3).
- **self_excluded** — terracotta ⌀ symbol. Used on the operator's transcribe surface (wf-10 §2.3) and on the audit-log operator surface.
- **kyc_verified** — small emerald check with *"verified"* label. Used on read-only pre-filled fields (wf-01 phone/email/DOB, wf-07 §4.1).

### 12.4 States

Single state per variant.

### 12.5 Tokens

- `color.brand.accent` — gold verified variant
- `color.state.success` — winner + kyc_verified variants
- `color.state.danger` — self_excluded variant

### 12.6 Accessibility

- Badges have `role="img"` with an accessible name matching the variant meaning.
- When paired with a label, badge is `aria-hidden` and the label carries the meaning.

### 12.7 Usage index

- verified: wf-06 §3 (reveal page ProofSummaryCard eyebrow), wf-14 §3.2 (VerdictCard), wf-09/11/12 §7 (receipts).
- winner: wf-05 §2.5, wf-05 §3.2, wf-06 §3.1 winning banner.
- self_excluded: wf-10 §2.3 (transcribe self-excluded state), wf-13 (audit-log actor context).
- kyc_verified: wf-01 §2.4 (phone/email/DOB verified pre-fill), wf-07 §4.1.

---

## 13. Empty state

### 13.1 Purpose

The container-level "there's nothing to show" pattern. Every listing / table / grid surface has an empty variant; this primitive is the shape of that variant.

### 13.2 Props

```
{
  illustration: "ticket" | "draw" | "search" | "note" | "custom_icon"
  headline:     string
  body:         string
  cta:          { label: string, onPress: () => void }   // optional
}
```

### 13.3 Layout

Centered vertical composition:
- 80pt circle in `surface.elevated` with an illustration/glyph inside (gold `brand.accent` colour).
- Space.600.
- Headline in `type.display.card` (24pt Fraunces).
- Body in `type.body.default` `color.text.secondary`.
- Space.800.
- Optional CTA (primary Button).

### 13.4 Tokens

- `color.surface.elevated` — illustration circle
- `color.brand.accent` — illustration glyph
- `type.display.card` — headline
- `type.body.default` — body
- `color.text.secondary` — body text

### 13.5 Accessibility

- Illustration is `aria-hidden="true"` (decorative).
- Headline is `<h2>` when the empty state occupies a page; `<h3>` when nested.
- CTA (if present) is a normal `Button`.

### 13.6 Usage index

- wf-02 §2.3 (no-active-draw home)
- wf-05 §2.2 (no tickets)
- wf-13 §2.3 (no events match filter — no illustration variant, just centered copy since the filter card carries visual context)

---

## 14. Error state

### 14.1 Purpose

Distinct from an error *banner* (§9). This is the "we couldn't load this page / section" pattern — a page-level or section-level fallback when a fetch has failed.

### 14.2 Props

```
{
  scope:      "page" | "section"
  headline:   string          // e.g. "We couldn't load your tickets."
  body:       string          // e.g. "Check your connection and try again."
  retry:      () => void
  supportContact: string      // optional; mailto: (V0.5) or WhatsApp link (V1)
}
```

### 14.3 Layout

Same vertical composition as empty state (§13), with:
- Icon: 48pt `⚠` glyph in `color.state.attention` (network) or `color.state.danger` (fatal).
- Headline in `type.display.card`.
- Body in `type.body.default` secondary.
- Retry `Button` (secondary variant).
- Optional support-contact inline link below.

### 14.4 States

- **Retrying** — Button enters loading state (per §3.4).
- **Retry succeeded** — the container above the error state re-renders.

### 14.5 Tokens

- `color.state.attention` / `color.state.danger` — glyph
- Same typography tokens as empty state.

### 14.6 Accessibility

- On mount: `role="alert"`.
- Retry button labelled clearly.
- Support contact link opens mail client on V0.5.

### 14.7 Usage index

- wf-02 §2.3 (draw detail fetch failed)
- wf-04 §5 (payment-result critical variant uses a specialised error-state with support-contact ref number)
- wf-05 §2.3 (tickets fetch failed)
- wf-06 (reveal page fetch failed)
- wf-08 §2.3 (admin login server error — banner variant, not full-page)
- wf-13 §2.3 (audit-log fetch failed)

---

## 15. Modal

### 15.1 Purpose

Centered dialog for confirmations and focused interactions. Every irreversible action (Cancel entry, Publish draw, Close draw, Reveal winner, Export unredacted) goes through a modal.

### 15.2 Props

```
{
  headline:     string
  eyebrow:      string          // optional gold uppercase label
  body:         ReactNode | string
  primaryCta:   { label: string, variant: "primary" | "danger", onPress: () => void, loading?: boolean }
  secondaryCta: { label: string, onPress: () => void }
  dismissOnBackdrop: boolean     // default true
  dismissOnEscape:  boolean     // default true
  typeToConfirm:    string       // if present, primary CTA disabled until user types this exact string
}
```

### 15.3 Layout

Centered, ~520pt wide on desktop, full-width minus 16pt margins on mobile. `radius.large`, `surface.base` fill, `elevation.2`, 32pt padding. Backdrop is `color.surface.inverted` at 60% opacity (warm-tinted, not pure black — same discipline as elevation shadows). Modal appears with fade + slight upward slide (60pt); reduce-motion mode uses fade only.

### 15.4 States

- **Default** — as drawn.
- **Primary CTA loading** — button loading state per §3.4.
- **Type-to-confirm empty / mismatched** — primary CTA disabled.
- **Type-to-confirm matched** — primary CTA enabled.
- **Dismissing** — animates out (fade + slight downward slide).

### 15.5 Tokens

- `radius.large` (12pt)
- `elevation.2`
- `color.surface.base` (modal fill)
- `color.surface.inverted` @ 60% (backdrop)
- All typography and button tokens as normal.

### 15.6 Accessibility

- `role="dialog"` `aria-modal="true"` `aria-labelledby="{headline-id}"`.
- Focus trap: on mount, focus goes to the first focusable element (usually the type-to-confirm input if present, else the primary CTA). Tab cycles within modal.
- Escape dismisses (equivalent to secondary CTA).
- Backdrop click dismisses (unless `dismissOnBackdrop` false).
- On dismiss, focus returns to the element that opened the modal.
- Type-to-confirm input: standard `<input type="text">` with `autocomplete="off"`; enabled/disabled state of primary CTA announced via `aria-live="polite"` helper span.

### 15.7 Usage index

- wf-04 §3.3 (Cancel entry confirmation)
- wf-08 §2.5 (login errors — banner, not modal)
- wf-09 §6 (Publish draw — type-to-confirm PUBLISH)
- wf-11 §3 (Close draw — type-to-confirm CLOSE)
- wf-12 §5 (Reveal winner — type-to-confirm REVEAL)
- wf-13 §3.6 (PII reveal reason prompt)
- wf-15 (self-exclusion confirmation flow references this pattern)

---

## 16. Toast

### 16.1 Purpose

Ephemeral notification of a completed micro-action. *"Commitment hash copied."*, *"Slip FE-04829 transcribed."*, *"New code sent."* — one-line acknowledgements that appear and dismiss automatically.

### 16.2 Props

```
{
  message:    string
  variant:    "default" | "success" | "attention" | "danger"    // default "default"
  duration:   milliseconds     // default 3000; longer for danger
  position:   "bottom" | "top"  // default "bottom" on mobile; "top-right" on desktop admin
}
```

### 16.3 Layout

Compact pill or short rectangle, `radius.medium`, `surface.inverted` (navy) fill, `color.text.inverted` (off-white) text, single line where possible. On mobile: 16pt above bottom safe area. On desktop admin: 16pt from top-right corner. Fade + slide-in on show; fade on dismiss.

### 16.4 Variants

- **default** — navy fill with off-white text. Most toasts.
- **success** — navy fill with a small `color.state.success` check icon prefix.
- **attention** — navy fill with `color.state.attention` icon prefix.
- **danger** — `color.state.danger` fill instead of navy; longer default duration (5s); dismiss button visible.

### 16.5 States

Show → visible for `duration` → auto-dismiss. Danger variant is dismissible manually.

### 16.6 Tokens

- `color.surface.inverted` (navy) — default fill
- `color.text.inverted` — text
- `color.state.*` — variant accents
- `radius.medium`
- `type.body.small` — text

### 16.7 Accessibility

- `role="status"` for default/success/attention.
- `role="alert"` for danger.
- Auto-dismiss timing is honoured but keyboard-focused users get a hover-to-persist behaviour (V1 refinement; V0.5 uses fixed duration).
- Multiple toasts stack vertically (max 3 visible; older ones auto-dismiss when a 4th appears).

### 16.8 Usage index

- Copy-hash toast: wf-02, wf-05, wf-06, wf-09, wf-11, wf-12, wf-13, wf-14.
- Save-slip toast: wf-10.
- New-code-sent toast: wf-01.
- Slip-voided toast: wf-10.
- Commitment/claim reference copied: wf-07.
- Sharing-arrives-with-V1 toast: wf-02, wf-05.

---

## 17. Nav bar

### 17.1 Purpose

Two variants under one primitive name (they share visual language and interaction discipline): the consumer mobile **bottom nav** and the admin desktop **sidebar nav**.

### 17.2 Props (bottom nav — consumer mobile)

```
{
  items:      NavItem[]      // 3 items in V0.5 (Draws, My tickets, Me)
  active:     string         // key of the active item
  onSelect:   (key) => void
}
```

Item shape:
```
{
  key:    string
  label:  string
  icon:   Icon
  badge:  integer | null    // optional unread-count chip
}
```

### 17.3 Props (sidebar nav — admin desktop)

```
{
  groups:     NavGroup[]     // "THIS WEEK" / "OPERATE" / "REVIEW" / "SETTINGS"
  active:     string         // key of the active item
  onSelect:   (key) => void
}
```

Group shape:
```
{
  label:  string      // uppercase gold eyebrow
  items:  NavItem[]
}
```

Item shape (sidebar):
```
{
  key:     string
  label:   string
  counter: integer | null      // trailing count chip (gold)
}
```

### 17.4 Layout

**Bottom nav (mobile):** full-width, 56pt tall, `surface.base` fill, hairline top border. 3 items with icon-above-label composition. Active item's icon in `color.brand.primary`; inactive in `color.text.secondary`. Bottom safe-area preserved.

**Sidebar nav (admin):** 240pt fixed width, `surface.elevated` fill, hairline right border. Groups with uppercase gold eyebrows (`label.micro`). Items are 40pt tall rows with 16pt left padding. Active item has a leading `→` in `color.brand.primary` and text in `text.primary`; inactive items have text in `text.secondary`. Hover subtle `surface.subtle` fill.

### 17.5 States

- **Default / inactive item.**
- **Active item.**
- **Hover (sidebar only).**
- **Focused** — 2pt focus ring around item.

### 17.6 Tokens

- `color.surface.base` — bottom nav fill
- `color.surface.elevated` — sidebar fill
- `color.divider.hairline` — borders
- `color.brand.primary` — active icon / active arrow
- `color.text.secondary` — inactive text
- `color.brand.accent` — sidebar group eyebrows + counter chips
- `type.label.micro` (uppercase) — sidebar eyebrow

### 17.7 Accessibility

- **Bottom nav:** `role="tablist"`; each item `role="tab"` with `aria-selected` bound to active state.
- **Sidebar nav:** proper landmark structure — `<nav aria-label="Admin sidebar">`; groups are `<h2>` + `<ul>`.
- Icons are `aria-hidden`; labels carry accessible names.
- Counter chip (sidebar): rendered as *"Draws, 1 active"* etc.

### 17.8 Usage index

- **Bottom nav:** wf-02 (Draws / My tickets / Me), wf-05.
- **Sidebar nav:** wf-08 §1 (established), wf-09, wf-10, wf-11, wf-12, wf-13.

---

## 18. Compositions catalog (one-off components not in the primitive set)

These names appear in the wireframes but are one-off compositions of the 15 primitives above. They are documented in their host wireframe and are not part of the design system. Amelia builds them as screen-specific compositions, not as reusable library primitives.

| Composition | Defined in | Composes |
|---|---|---|
| `TicketArtefact` (winning + standard variants) | wf-05 §3 | Ticket card §5 + hash rows + perforated divider + gold accents |
| `VerdictCard` (public proof) | wf-14 §3.2 | Verification badge §12 + headline + body |
| `CommitmentReceiptCard` | wf-09 §7 | Empty state pattern + hash rows + definition list + button |
| `CloseReceipt` | wf-11 §4 | Same shape as CommitmentReceiptCard |
| `RevealReceipt` | wf-12 §6 | Same shape + additional entropy + winner blocks |
| `StepList` (ceremony steps) | wf-12 §2, §3 | Ordered list with per-step state icons + inline results |
| `ChainStateBanner` | wf-13 §2.1 | Banner §9 specialised for chain state |
| `MatchResultCard` | wf-10 §2.2 | Specialised card variant with state colour |
| `TrustSectionCard` / `TrustCallout` | wf-15 §1.1 | Cards with gold-bulleted / left-bordered treatment |
| `CommitmentSummaryCard` | wf-12 §2 | Hash rows + timing rows in a summary card |
| `WarningNote` | wf-09 §4.2, wf-11 §2.1, wf-15 Part B §3 | Banner §9 with attention treatment |
| `InfoNote` | wf-04 §3.1, wf-14 (informational blocks) | Card with gold bullet + body |
| `ProgressIndicator` (3-dot / 4-dot) | wf-07 §3.1, wf-09 §3 | Simple dot-progress line |
| `ConsentCard` | wf-07 §7.5 (post-amendment) | Card with checkbox + explanation |
| `ReviewSection` | wf-07 §7.5, wf-09 §5.3 | Card with eyebrow + summary + Edit link |
| `OrderCard` | wf-04 §3.1 | Card with draw summary + line items + total |
| `SplashCheck` | wf-01 §5, wf-04 §5, wf-07 §8 | Gold check + label + subtext, centered |
| `StatusTimeline` | wf-07 §8.1 | Vertical stage list with per-stage dots |
| `PoolSummaryCard` | wf-11 §2, wf-14 §3.4 | Total + paid/free breakdown + timing rows |
| `QuestionPreviewCard` | wf-09 §4.1 | Preview of a skill question with answers listed |
| `ProofSummaryCard` | wf-06 §3.1 | Card with commitment / seed / winner-ticket rows |
| `ReplayVerificationCard` | wf-12 §4.1 | Verifier inputs + result confirmation |
| `CandidateWinnerCard` | wf-12 §4.1 | Card with winner profile + SE check + KYC status |
| `ReservesList` | wf-12 §4.1 | Ordered list of reserve tickets |
| `DrawCardPreview` | wf-09 §5.3 | Wraps Draw card §6 with admin preview context |
| `HashRow` | wf-02 §3, wf-05 §3, wf-09 §7, wf-11 §4, wf-12 §6, wf-13 §3, wf-14 §3.3 | Label + mono hash + copy affordance |
| `LoginCard` | wf-08 §2 | Centered card with logo + form + footer |
| `FormGroupCard` | wf-09 §3, wf-10 §2 | Bordered card grouping related fields |
| `AdminTopBar` | wf-08 §1 (shell) | Admin header |
| `AdminSidebar` | wf-08 §1 (shell) | Sidebar nav §17 specialised for admin |
| `NotificationBanner` | wf-06 §2 | Banner §9 for on-launch reveal notifications |
| `NotificationRow` | wf-06 §4 | Table row §8 for notification history |
| `TicketReferenceRow` | wf-06 §3 | Ticket number + outcome + purchase metadata |
| `RequirementCard` | wf-07 §2 | Card with numbered list of requirements |
| `AfterPublishExplainer` / `AfterCloseExplainer` | wf-09 §5, wf-11 §2 | Numbered list of consequences |
| `SummaryStrip` | wf-10 §2 | Draw-summary strip for admin |
| `RelatedLinksRow` | wf-15 §1.1 | Three cross-links |
| `ContactLine` | wf-15 §1.1 | One-line contact footer |
| `SidePanel` | wf-13 §3 | Side-panel container for admin details |
| `PayloadViewer` | wf-13 §3 | JSON payload viewer with PII redaction |
| `RelatedEventsList` | wf-13 §3 | Compact list of related audit events |
| `AlgorithmCard` / `VerifierCard` | wf-14 §3.6, §3.7 | Cards holding algorithm / verifier content |

**Rule of thumb (§1 principle 10):** if a composition appears in 3 or more wireframes across 3 or more distinct contexts, promote it to a primitive. Currently the primitive set is 15; no composition above meets the promote-threshold.

---

## 19. What the design system deliberately does NOT include (for V0.5)

- **Animation library.** V0.5 uses default platform easings and a 150ms baseline duration. Motion tokens land in V1 when we have real motion moments to name.
- **Iconography library.** V0.5 uses a small set of standard icons (chevron, check, ✕, ⚠, ⌀, ●, ▪, ○). Icon primitive is trivial; formal library is V1.
- **Colour palette expansion beyond `tokens.md`.** No `color.red.500`-style ramps; every colour has a semantic name.
- **Multiple font families beyond Fraunces / Inter / JetBrains Mono.** Adding a fourth is a deliberate design amendment.
- **Grid system.** V0.5 uses Flutter's default layout primitives (Row, Column, Padding) + Next.js's default layout (flex/grid). A formal 12-column grid is a V1+ concern when the surface grows.
- **Dark mode.** Tokens accommodate a future dark mode without rename per `tokens.md §1.5`. V0.5 ships light-mode only.
- **Themeable branding.** Atlas is one brand for V0.5; a themeable design system for multi-brand deployment is a V2+ concern.

---

## 20. Amelia handoff notes

### 20.1 Where components live in code (recommended)

Flutter — `mobile/lib/design/`:
- `mobile/lib/design/tokens/` — colour, spacing, typography, radius, elevation constants generated from `tokens.md`.
- `mobile/lib/design/components/` — the 15 primitives.
- `mobile/lib/design/compositions/` — screen-specific compositions.

Next.js — `web/src/design/`:
- `web/src/design/tokens/` — CSS custom properties + Tailwind theme extension.
- `web/src/design/components/` — the 15 primitives as React components.
- `web/src/design/compositions/` — screen-specific compositions.

### 20.2 Build order (recommended)

Week 3 identity module needs: Button, Input (all variants), Banner, Modal, Toast, Nav bar (bottom). Build those first.

Week 4 wallet + payment needs: Draw card, Ticket card, Order card composition. Build next.

Week 5 ticket module needs: Skill-question card, Payment confirmation states.

Week 6 draw engine needs: Timer, Table row, Audit-log row, Verification badge, Empty state, Error state. Build alongside admin surfaces.

Week 7 polish + proof page needs: everything above already built, plus the compositions specific to the proof page (VerdictCard, AlgorithmCard, VerifierCard).

### 20.3 What to ping Sally about

- If a wireframe references a component or composition not documented here (either primitives §3-17 or compositions §18), it's a bug in this document — ping me.
- If two wireframes render the same composition with different behaviour, treat it as a bug and reconcile with me before implementing.
- If a primitive's contract feels too rigid for a specific screen, don't work around it in that screen's code — that produces silent divergence. Ping me for a design amendment.

### 20.4 What to ping Winston about

- Cross-platform contract points (data models, event shapes) where Flutter and Next.js consume the same data.
- ADR-level architectural decisions that would affect component behaviour (e.g. if the ticket-issuance state machine changes shape, the Ticket card variants need to change).

### 20.5 What to ping Adaeze about

- Any change to compliance-adjacent copy in a component's default rendering.
- Any change to the redaction / consent behaviour on the audit-log row, ticket detail, claim form, or public proof page.

---

## 21. Cross-references

- Tokens (authoritative): `tokens.md`.
- Tone + voice: `tone-doc.md`.
- Every wireframe under `_bmad-output/planning-artifacts/design/wireframes/01..15` composes from this system.
- Compliance review: `docs/compliance/reviews/REVIEW-001-v0.5-consumer-wireframes.md` — the WarningNote and ConsentCard compositions specifically answer REVIEW-001 findings.
- Agent operating model: `docs/AINE-AGENTS.md` — this artefact is a design→dev handoff per §4 artefact registry.

---

🎨 *End of components.md. Day 13 complete.*

*The 15 primitives are specified; the compositions are catalogued and cross-referenced to their host wireframes; the handoff notes to Amelia are on the record. Day 14 tomorrow — Week 2 exit gate. Founder end-to-end review of everything (tone + tokens + wireframes 01-15 + REVIEW-001 + Week-1 checkpoint + this) and handoff to Amelia for Week 3 build start.*

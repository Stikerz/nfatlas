# Wireframe 02 — Browse Active Draw (Home + Draw Detail)

**Drafted:** 2026-07-08 (Day 4 per `tone-doc.md §8`)
**Drafted by:** 🎨 Sally (BMad UX Designer)
**Status:** Draft — pending founder review at end of Week 1.
**Covers:** Flagship flow step 2 from `v0.5-demo-plan.md §2` — *"Browse the active draw — one draw configured in seed data. Prize (cash ₦2M or a car photo), close time, current entry count (paid + free split visible)."*
**Surface:** Flutter consumer app.
**Pairs with:** `03-free-entry-disclosure.md` (the disclosure element on the draw detail page — separated for reviewability), `tokens.md`, `tone-doc.md`, `v0.5-demo-plan.md`.

---

## 0. Why this flow, second

After registration (wireframe 01), the user arrives here. This is the first screen where the *product* has to earn its keep — she has just handed over an email, a phone, and a password. What she is looking at now must feel worth that friction.

Two design forces meeting on this screen:

1. **Aspiration.** The prize is the hero (tone-doc.md §1, Anchor 1 BOTB). She must feel *this is a real thing I could actually win.*
2. **Integrity.** Every trust element (entry count breakdown, close-time absolute, free-entry route visible without hunting) is present *on the primary browse surface* — not buried behind a "Learn more" tab. Trust doesn't live on a separate page; it's threaded through the product.

**Non-goals for V0.5:**
- Multiple concurrent draws (per `v0.5-demo-plan.md §3` — one seed draw only).
- Search, filter, sort. There's one draw. Nothing to search.
- Personalisation, recommendations. V1.
- "Previous winners" carousel on home. V1 marketing surface.
- Live entry-count animation (ticking up in real-time). V1 polish; V0.5 refreshes on pull-to-refresh.

---

## 1. Flow overview

```
┌──────────────┐      ┌──────────────┐
│  Screen 2.1  │─────▶│  Screen 2.2  │
│  Home (list) │      │  Draw detail │
│  1 active    │      │  full-bleed  │
│  draw card   │      │  prize page  │
└──────────────┘      └──────────────┘
                              │
                              │ tap: "How the free route works"
                              ▼
                     ┌──────────────┐
                     │  Sheet 2.3   │  ← disclosure sheet
                     │  (covered in │      (short summary; the full
                     │   wf-03)     │       detail page is Day 12)
                     └──────────────┘
                              │
                              │ tap: "Enter"
                              ▼
                       (→ wireframe 04 — skill question)
```

Two primary screens. One modal sheet. The disclosure sheet gets its own wireframe file (`03`) because it's the *most-scrutinised* piece of UI on the draw page for compliance and trust reasons — separating it makes review cheaper.

---

## 2. Screen 2.1 — Home

### 2.1 Layout (Flutter — mobile portrait, 375pt reference width)

```
┌─────────────────────────────────────────┐
│                                         │  ← status bar
│                                         │
│  Atlas              👤 Adaeze  ▾        │  ← app bar, 56pt.
│                                         │      Left: wordmark (Fraunces 20pt).
│                                         │      Right: greeting chip + menu chevron.
│                                         │
├─────────────────────────────────────────┤  ← divider.hairline
│                                         │
│                                         │  space.600
│                                         │
│  This week's draw                       │  ← type.label.micro (uppercase, gold)
│                                         │      color.brand.accent
│                                         │
│                                         │  space.300
│                                         │
│  ┌───────────────────────────────────┐ │  ← DrawCard (see §2.2 components)
│  │                                   │ │      radius.large, elevation.1
│  │  ┌─────────────────────────────┐ │ │      surface.elevated
│  │  │                             │ │ │
│  │  │   [ Prize photograph ]      │ │ │  ← 4:3 aspect, radius.large top,
│  │  │                             │ │ │      square bottom (image sits
│  │  │                             │ │ │      flush inside card top edge)
│  │  └─────────────────────────────┘ │ │
│  │                                   │ │
│  │  ₦2,000,000                       │ │  ← type.display.hero (64pt Fraunces)
│  │                                   │ │      color.text.primary
│  │                                   │ │
│  │  in cash                          │ │  ← type.body.default, secondary
│  │                                   │ │
│  │  ─────────────────────────────    │ │  ← hairline
│  │                                   │ │
│  │  Closes 8pm Saturday              │ │  ← type.body.default, primary
│  │  1,247 entries · 87 free-route    │ │  ← type.body.small, secondary
│  │                                   │ │
│  │  ┌─────────────────────────────┐ │ │
│  │  │           View draw         │ │ │  ← button, secondary variant
│  │  └─────────────────────────────┘ │ │      (outline navy on surface)
│  │                                   │ │      52pt tall, full width in card
│  └───────────────────────────────────┘ │
│                                         │
│                                         │  space.1200
│                                         │
│  ─────────────────────────────────      │  ← hairline
│                                         │
│  How Atlas works →                      │  ← link row, body.default, navy
│  Responsible play →                     │
│  Terms and Privacy →                    │
│                                         │
│                                         │  bottom nav or safe area
├─────────────────────────────────────────┤
│  🏠 Draws    🎟 My tickets    👤 Me     │  ← bottom nav (3 tabs, V0.5)
└─────────────────────────────────────────┘
```

### 2.2 Components used

- `AppBar` — wordmark left, greeting-chip + chevron right (opens `Me` overflow — sign out, self-exclusion, help).
- `SectionLabel` — the "This week's draw" gold eyebrow.
- `DrawCard` — the hero component of the home screen. Composes: `PrizePhotograph` (4:3 media block), `PrizeAmount` (Fraunces hero), `PrizeUnit` (body secondary), `Divider.hairline`, `CloseTimeLine` (body primary), `EntryCountLine` (body small secondary), `Button` (secondary variant).
- `LinkRow` — repeated 3× for the trust-story anchors.
- `BottomNav` — 3 tabs.

### 2.3 States

**Default (as drawn).** V0.5 has exactly one active draw seeded, so this state is what the founder shows in demo.

**Loading (initial fetch):** DrawCard renders as a skeleton — image block is a `surface.elevated` rectangle, prize amount is a 240×48 shimmer, close-time / entry-count are grey rectangles. Skeleton, not spinner — feels like a real product, not a boot screen. Duration: <500ms typical; skeleton persists min 200ms to avoid flash.

**Loading (pull-to-refresh):** iOS-style rubber-band pull triggers the refresh. Small `brand.accent` spinner shows at the top; card content updates in place without a full re-render.

**Empty (no active draws — should not occur in V0.5 demo but implemented for robustness):**
- Illustration slot (`surface.elevated` circle with a subtle Atlas mark).
- Copy: *"Nothing running right now. The next draw opens Friday morning."*
- No CTA — deliberate; there is nothing to do. Nudge: subscribe for notifications (deferred to V1; V0.5 shows the empty state without action).

**Error (network fetch failed):**
- Banner at top: *"We couldn't load the draw. Pull to try again."*
- Card region shows a placeholder card with retry chip.

**Draw closed (post-close, pre-reveal — visible in demo if founder closes draw during walkthrough):**
- Section label switches from "This week's draw" to "This draw has closed."
- Prize amount stays.
- Close-time line replaced by: *"Sales closed 8pm Saturday. Winner announced 9pm Sunday."*
- Button label becomes *"View draw"* (unchanged) — but on tap, draw-detail shows post-close state (see §3.3).

**Draw revealed (post-reveal):**
- Section label: *"This draw is complete."*
- Prize amount replaced by winner-name treatment: *"₦2,000,000 won by Ifeoma A. — Yaba."*
- Button: *"See the proof."* (navigates to public verification page — flagship step 14, wireframe 12).

### 2.4 Copy

| Element | Copy |
|---|---|
| Section eyebrow (open) | This week's draw |
| Section eyebrow (closed) | This draw has closed |
| Section eyebrow (revealed) | This draw is complete |
| Prize amount (cash) | ₦2,000,000 |
| Prize unit line | in cash |
| Close-time line (open) | Closes 8pm Saturday |
| Close-time line (closed) | Sales closed 8pm Saturday. Winner announced 9pm Sunday. |
| Close-time line (revealed) | Winner announced 9pm Sunday. |
| Entry-count line | 1,247 entries · 87 free-route |
| CTA (all states) | View draw |
| CTA (post-reveal) | See the proof |
| Empty state | Nothing running right now. The next draw opens Friday morning. |
| Error banner | We couldn't load the draw. Pull to try again. |
| Trust-story links | How Atlas works · Responsible play · Terms and Privacy |
| Greeting chip | 👤 {first_name} |

**Copy commentary:**
- *"in cash"* as a separate line under the prize amount lets the amount typeset huge without a unit crowding it. Amounts always have `₦` and thousands separators (tone-doc.md §5).
- *"1,247 entries · 87 free-route"* is the single most important trust element on the home surface. Every draw page, every card, always shows the split. **This is a compliance-and-tone commitment, not a data readout.** It says: the free route is real, we count it, we show you the count.
- Timestamps absolute (*"8pm Saturday"*, not *"in 2 days"*) — tone-doc.md §5.

### 2.5 Accessibility

- **Focus order:** AppBar wordmark → Greeting chip → SectionLabel (non-interactive, skipped) → DrawCard (composite, focused as a single actionable region on tap) → View-draw button → Trust-story links (3) → BottomNav tabs.
- **DrawCard as a11y group:** the entire card is a single tap target for keyboard/screen-reader users (as well as the explicit button). Card has `role="link"` (web) / `Semantics(button:true)` (Flutter) with a composed label: *"This week's draw. ₦2,000,000 in cash. Closes 8pm Saturday. 1,247 entries, 87 via the free route. View draw."*
- **Prize photograph alt text:** authored per prize. Seed draw: *"A stack of new ₦1,000 notes on a warm wooden surface."* Not decorative — reads to screen reader.
- **Section eyebrow contrast:** gold on off-white is `2.6:1` — this is *the reason* it's used as a `type.label.micro` (12pt, uppercase, letter-spaced) which meets AA large-text via weight + spacing. If founder is uncomfortable with this at all, we swap eyebrow to `color.text.secondary` (7:1) — small tone loss, easy call.
- **Touch targets:** DrawCard ≥ 500pt tall; button 52pt; nav tabs 48pt.
- **Bottom nav labels:** always shown (no icon-only). Icons + labels helps discoverability.

### 2.6 Interaction notes

- **Card tap:** navigates to Screen 2.2 (draw detail) with `SlideUp` transition (300ms, ease-out) — the "prize rises to hero" motion. The prize photograph and amount are Hero-animated across screens (Flutter `Hero` widget).
- **Pull to refresh:** re-fetches entry count + close-time. Card gently updates in place.
- **Overflow menu (greeting chip chevron):** sheet with Sign out, Self-exclusion, Help. V0.5 self-exclusion is stubbed per plan but the entry point exists.

---

## 3. Screen 2.2 — Draw detail

### 3.1 Layout

```
┌─────────────────────────────────────────┐
│                                         │
│  ← Back                          🔗     │  ← top bar, transparent overlay
│                                         │      (share icon; V0.5 shows toast
│                                         │       "Sharing coming soon")
│                                         │
│  ┌───────────────────────────────────┐ │
│  │                                   │ │
│  │                                   │ │
│  │                                   │ │  ← FULL-BLEED prize photograph
│  │       [ Prize photograph ]        │ │      Aspect: 4:3, extends edge-to-edge
│  │                                   │ │      Height: ~50% of viewport
│  │                                   │ │      No card, no radius, no shadow
│  │                                   │ │
│  │                                   │ │
│  └───────────────────────────────────┘ │
│                                         │
│                                         │  space.800 (32pt)
│                                         │
│  This week's draw                       │  ← eyebrow gold uppercase
│                                         │  space.200
│                                         │
│  ₦2,000,000                             │  ← type.display.hero (64pt Fraunces)
│                                         │
│  in cash                                │  ← body.default, secondary
│                                         │  space.600
│                                         │
│  ─────────────────────────────          │  ← hairline
│                                         │  space.400
│                                         │
│  ⏱  Closes 8pm Saturday, 12 July        │  ← Row: icon + body.default, primary
│                                         │      countdown live below in secondary
│  Closes in 3 days, 8 hours              │      (relative countdown — allowed
│                                         │       here as SUPPORTING info; the
│                                         │       absolute time is primary)
│                                         │  space.400
│                                         │
│  🎟  1,247 entries so far               │
│      1,160 paid · 87 via free route     │  ← body.small, secondary
│                                         │  space.400
│                                         │
│  🔐  Draw commitment hash               │
│      3f2c…8a91  📋                      │  ← body.mono (JetBrains Mono 14pt)
│                                         │      copy-to-clipboard icon inline
│                                         │  space.400
│                                         │
│  ┌───────────────────────────────────┐ │  ← FreeEntryDisclosure — see wf-03
│  │  ▪ Free entry route                │ │      radius.large, surface.elevated,
│  │                                    │ │      elevation.0, hairline border
│  │  Prefer not to pay? Every draw     │ │
│  │  offers a free postal entry.       │ │
│  │  Same odds, same pool, same shot.  │ │
│  │                                    │ │
│  │  How the free route works →        │ │  ← inline link opens sheet 2.3
│  └───────────────────────────────────┘ │
│                                         │
│                                         │  space.800
│                                         │
│  About this draw                        │  ← type.display.card (24pt Fraunces)
│                                         │
│  The winner receives ₦2,000,000 paid    │  ← body.default
│  by bank transfer within 5 working      │
│  days of the reveal.                    │
│                                         │
│  Prize competition operated by Atlas    │
│  Africa Ltd. Winner determined by       │
│  provably-fair draw — see the           │
│  verification page after the reveal.    │
│                                         │  space.1200
│                                         │
│                                         │
│  (sticky footer, see below)             │
│                                         │
└─────────────────────────────────────────┘

  ┌─────────────────────────────────────┐ │
  │  ₦2,500 per entry                   │ │  ← sticky footer, elevation.1,
  │  ┌───────────────────────────────┐ │ │      surface.base with top hairline.
  │  │           Enter                │ │ │      Always visible on scroll.
  │  └───────────────────────────────┘ │ │      Button = primary, full width.
  └─────────────────────────────────────┘ │
```

### 3.2 Components used

- `TopBar` — transparent overlay variant on top of the photograph; back arrow + share icon.
- `PrizePhotograph` — full-bleed variant (no card, no radius).
- `SectionLabel` — gold eyebrow.
- `PrizeAmount` — hero size.
- `MetaRow` — icon + label + value composition, reused 3× (close time, entry count, commitment hash).
- `HashDisplay` — mono + copy-to-clipboard icon.
- `FreeEntryDisclosure` — the disclosure box (full spec in `03-free-entry-disclosure.md`).
- `Divider.hairline`.
- `SectionHeadline` — "About this draw" 24pt Fraunces.
- `StickyFooter` — price + primary CTA.

### 3.3 States

**Open (as drawn).** Sticky footer active; Enter navigates to skill question (wireframe 04, Day 5).

**Approaching close (< 4 hours remain):**
- Countdown line switches to `color.state.attention` (muted amber): *"Closes in 3 hours 24 minutes"*.
- No urgency badges, no red timers, no flashing. Copy alone signals attention.

**Closed (post 8pm Saturday, pre-reveal):**
- Sticky footer replaces button with a static line: *"Sales closed 8pm Saturday. Winner announced 9pm Sunday."*
- Section eyebrow changes to *"This draw has closed."*
- Entry-count line freezes with final count: *"Final: 1,247 entries · 1,160 paid · 87 via free route."*
- Commitment hash still shown; joined by a *"Awaiting reveal"* status chip below hash.
- Free-entry disclosure box switches copy to: *"Sales closed. The free route accepted 87 entries this draw."*

**Revealed (post 9pm Sunday):**
- Section eyebrow: *"This draw is complete."*
- Hero swaps: prize photograph is replaced by a documentary portrait of the winner (V0.5: for demo, seeded winner portrait — real winners in V1 with consent capture flow).
- Copy block above hero: *"Won by Ifeoma A. — Yaba."* (Fraunces display.section, `color.text.accent` — winner name in gold, on off-white this is `text.primary` for contrast; the celebration is in typography not colour).
- Sticky footer replaced with: *"See how the draw was verified →"* linking to public proof page.

**Loading:** skeleton on first fetch (photograph shimmer, amount block, meta rows). <500ms typical.

**Error (fetch failed):** page-level banner *"We couldn't load this draw. Pull to try again."*; skeleton remains until refresh.

### 3.4 Copy

| Element | Copy |
|---|---|
| Section eyebrow (open) | This week's draw |
| Prize amount | ₦2,000,000 |
| Prize unit | in cash |
| Close time (absolute) | Closes 8pm Saturday, 12 July |
| Close time (relative sub) | Closes in 3 days, 8 hours |
| Close time (< 4h) | Closes in 3 hours 24 minutes |
| Close time (closed) | Sales closed 8pm Saturday. Winner announced 9pm Sunday. |
| Entry count line | 1,247 entries so far |
| Entry count breakdown | 1,160 paid · 87 via free route |
| Entry count (closed) | Final: 1,247 entries · 1,160 paid · 87 via free route |
| Hash label | Draw commitment hash |
| Free-entry disclosure title | Free entry route |
| Free-entry disclosure body | Prefer not to pay? Every draw offers a free postal entry. Same odds, same pool, same shot. |
| Free-entry inline link | How the free route works |
| Free-entry (closed) | Sales closed. The free route accepted 87 entries this draw. |
| About headline | About this draw |
| About body 1 | The winner receives ₦2,000,000 paid by bank transfer within 5 working days of the reveal. |
| About body 2 | Prize competition operated by Atlas Africa Ltd. Winner determined by provably-fair draw — see the verification page after the reveal. |
| Sticky price | ₦2,500 per entry |
| Sticky CTA | Enter |
| Sticky (closed) | Sales closed 8pm Saturday. Winner announced 9pm Sunday. |
| Share toast (V0.5) | Sharing arrives with V1. Copy the link if you want to send it now. |

**Copy commentary:**

- *"Prize competition operated by Atlas Africa Ltd. Winner determined by provably-fair draw — see the verification page after the reveal."* — this is the compliance-load-bearing sentence on the draw detail page. **Adaeze review required** before wireframes exit Week 1. She will confirm phrasing satisfies the Nigerian prize-competition framing per `_bmad-output/planning-artifacts/research/domain-nigerian-prize-competition-licensing-research-2026-06-30.md`.
- The hash treatment (label + truncated hash + copy icon) borrows directly from Anchor 5 (Coinbase proof). This is the first appearance of the hash motif in the consumer journey; it recurs at reveal, in "My tickets", and lives centrally on the proof page (Day 11).

### 3.5 Accessibility

- **Focus order (open state):** Back → Share → Prize photograph (announced with alt text; not focusable as a tap target — it's decorative-informative, not interactive) → Prize amount region (composite readable label: *"This week's draw. Two million naira in cash."*) → Close time row → Entry count row → Commitment hash row (with "Copy hash" as the interactive element inside it) → Free-entry disclosure (composite region with the inline link as the interactive element) → About section → Sticky Enter button.
- **Sticky footer:** announced as *"Enter this draw. Two thousand five hundred naira per entry."* — kept out of screen-reader focus flow of the scrolling content (so the user doesn't hear it twice) but reachable via the "landmarks" list.
- **Hash region:** the truncated hash is read literally as *"3 f 2 c dot dot dot 8 a 9 1"* — the copy button announces *"Copy full hash to clipboard"* and on tap the confirmation is announced.
- **Alt text on photograph:** authored per prize; for cash it's a warm-lit stack of notes, not stock imagery. For a car it's the car in Nigerian light per tone-doc.md §7.
- **Reduce motion:** Hero animation on card→detail transition disabled; simple cross-fade.
- **Contrast:** all pairings on tokens; the gold section eyebrow is 12pt uppercase with tracking — passes AA large text on off-white via the weight/spacing exception (§2.5 note applies).

### 3.6 Interaction notes

- **Enter button:** navigates to skill question screen (wireframe 04, Day 5).
- **Free-entry disclosure link tap:** opens bottom sheet 2.3 (see `03-free-entry-disclosure.md §3`). Sheet closes to return to this page; no state loss.
- **Copy hash:** copies full 64-char hash to clipboard; toast *"Commitment hash copied."*
- **Share (V0.5 stub):** toast per copy table. In V1 this becomes a proper share sheet with pre-composed message.
- **Scroll behaviour:** on scroll, the transparent top-bar back-arrow gets a `surface.base` circle background (with `elevation.1`) at ~120pt scroll depth, so it stays legible as the photograph scrolls out of view. Standard iOS/Material pattern.
- **Pull to refresh:** re-fetches entry count and close-time. Photograph does not re-fetch.
- **Countdown ticking:** relative-countdown sub-line updates every minute (never every second — visual noise). Absolute line never changes.
- **Deep link:** the draw detail is deep-linkable via `atlas://draw/{draw_id}` (V0.5) and `https://atlas.ng/draw/{draw_id}` (public URL, V1). V0.5 supports the atlas:// scheme for demo; https:// URL routes to the public marketing site (out of V0.5 scope).

---

## 4. Cross-flow notes

- **From here to Enter (wireframe 04):** Enter button posts an idempotency-keyed "start entry" call; user proceeds to skill question. State handoff carries `draw_id` and a freshly-issued `entry_attempt_id`.
- **From here to the free-entry sheet (wireframe 03):** informational-only; no state handoff. Sheet returns to this page.
- **Post-reveal linkage:** the "See the proof" and "See how the draw was verified" links point to the public proof page (Day 11).
- **My tickets link:** if the user has already entered this draw, an inline chip appears above the Enter button: *"You have 2 tickets in this draw. See tickets."* — chip navigates to My tickets (flagship step 5, wireframe 05, Day 5). V0.5 supports this because the entry state is real.

---

## 5. Open questions for founder review

1. **Prize photograph for cash prize.** Recommendation is a warm-lit stack of new ₦1,000 notes on wood (not stock). Real photography, shot for Atlas. If we can't get a shoot in the V0.5 window, fallback is a neutral abstract *"cash"* mark rather than any stock imagery — stock destroys the trust story.
2. **Gold eyebrow contrast.** Currently 2.6:1 on off-white, permitted by AA large-text via 12pt uppercase + tracking. If you'd rather play it safe, we swap to `color.text.secondary` grey; loses a small warmth beat.
3. **Sticky footer treatment when closed** — currently a static text line replaces the button. Alternative: show a *"See who won"* button (post-reveal). Currently that's rendered as a link in the "About" area — considered a link, not a button. Prefer the current call; open to challenge.
4. **Deep-link scheme.** V0.5 uses `atlas://`. If you'd prefer we not register a custom scheme yet (to avoid store-review friction later), we can use in-app-only navigation for V0.5. Recommend keep — it costs nothing and supports founder-demo of a "link a ticket to a person" flow via URL.
5. **"1,160 paid · 87 via free route" ordering** — paid listed first because it's the larger number. In an integrity-first product, should free-route be first (visually asserted, not just present)? I currently think paid-first because larger-first reads as honest data, not persuasive framing. Open to challenge.

---

## 6. Cross-references

- Flow source: `v0.5-demo-plan.md §2` (step 2).
- Companion wireframe: `03-free-entry-disclosure.md` — the disclosure element and its bottom sheet.
- Tokens: `tokens.md`.
- Tone: `tone-doc.md` — Anchor 1 (BOTB) hero treatment, Anchor 3 (Range Rover) object-of-affection posture, Anchor 5 (Coinbase) hash typography.
- Compliance copy owner: ⚖️ Adaeze — must review the "About this draw" compliance sentence and the free-entry disclosure copy before Week 1 exit.
- Backend contract: 💻 Amelia (Week 5 ticket module + Week 6 draw engine) — `draw_id`, `commitment_hash`, `entries_paid`, `entries_free`, `close_time`, `reveal_time`, `entry_price_naira`.

---

🎨 *End of wireframe 02. Continues in `03-free-entry-disclosure.md`. Day 5 (skill question + payment + ticket appears) tomorrow.*

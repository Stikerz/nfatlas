# Wireframe 05 — My Tickets (list + detail — Anchor 3 moment)

**Drafted:** 2026-07-08 (Day 5 per `tone-doc.md §8`)
**Drafted by:** 🎨 Sally (BMad UX Designer)
**Status:** Draft — pending founder review at end of Week 1. **Extra design attention** per `tone-doc.md §8` Day 5 — this is the Anchor 3 "object of affection" moment.
**Covers:** Flagship flow step 5 from `v0.5-demo-plan.md §2` — *"View ticket — ticket number, purchase timestamp, entry source ('paid')."*
**Surface:** Flutter consumer app.
**Pairs with:** `04-buy-ticket-skill-payment.md` (the flow that lands here), `tokens.md`, `tone-doc.md` (Anchor 3 Range Rover configurator).

---

## 0. Why this screen carries more design load than any other consumer screen

Every other consumer screen in V0.5 is *functional* — register, browse, buy, receive notification, view proof. This one is *emotional*.

The prompt from tone-doc.md §2 Anchor 3 (Range Rover Configurator) is specific: *"When a user has bought a ticket and is looking at 'My Tickets,' there should be a moment of ownership that mirrors the feeling of specifying a car you haven't bought yet. Not a receipt. An artefact."*

**A ticket on Atlas is a small object the user feels affection for.** That is the design goal. Not clarity of information (though it must have that). Not utility (though it must have that). **Ownership feel.**

This changes how the screen is built:
- The ticket card is not a table row. It is a bounded, distinct visual object.
- The ticket card is not a receipt. Receipts sum things up; artefacts *are* the thing.
- The ticket card carries the trust story — commitment hash, entry source, timestamp — but does it as *provenance*, the way a limited-edition print carries its edition number, not as *disclaimer*.
- The ticket card must survive a screenshot to WhatsApp. The user will show her sister that she entered. What she shows must not embarrass her.

Everything below serves the above.

**Non-goals for V0.5:**
- Sharing to social. V1.
- Ticket "gifting" (transfer to another user). Never in V1; regulatory.
- Multi-draw view (tabs by draw). One active draw in V0.5, so a single list suffices.
- QR code on ticket. Not needed for V0.5's digital-only flow; possibly V1 if physical redemption is ever a thing.

---

## 1. Flow overview

```
                        (from wireframe 04 §5
                         "See your tickets")
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │  Screen 5.1          │
                        │  My tickets (list)   │
                        │  1..N ticket cards   │
                        │  grouped by draw     │
                        └──────────┬───────────┘
                                   │ tap a card
                                   ▼
                        ┌──────────────────────┐
                        │  Screen 5.2          │
                        │  Ticket detail       │
                        │  the artefact        │
                        └──────────────────────┘
```

Two screens. The list is a set; the detail is a single ticket in isolation. The detail is where Anchor 3 lives — the list is a well-designed set of them.

---

## 2. Screen 5.1 — My tickets (list)

### 2.1 Layout — with tickets

```
┌─────────────────────────────────────────┐
│                                         │  ← status bar
│                                         │
│  ← Back                       Refresh   │  ← top bar
│                                         │
│                                         │  space.600
│                                         │
│  My tickets                             │  ← type.display.section (40pt Fraunces)
│                                         │
│                                         │  space.400
│                                         │
│  ▪ Active — closes 8pm Saturday         │  ← section label, gold uppercase
│                                         │
│                                         │  space.400
│                                         │
│  ┌───────────────────────────────────┐ │  ← TicketCard, radius.large,
│  │                                    │ │      elevation.1, surface.elevated,
│  │  ▪ Atlas — Ticket                  │ │      120pt tall (compact list variant)
│  │                                    │ │
│  │  04829                             │ │  ← body.mono, 32pt (larger than default
│  │                                    │ │      mono — this IS the reason for the
│  │                                    │ │      card's existence)
│  │  ─────────────────────────         │ │  ← hairline (subtle divider inside card)
│  │                                    │ │
│  │  ₦2,000,000 in cash                │ │  ← body.default, primary
│  │  Purchased 8 July, 14:23           │ │  ← body.small, secondary
│  │                                    │ │
│  │  ✓ Paid entry                      │ │  ← body.small, success (subtle)
│  └───────────────────────────────────┘ │
│                                         │  space.400
│  ┌───────────────────────────────────┐ │
│  │  ▪ Atlas — Ticket                  │ │
│  │  04830                             │ │  ← second ticket (if user has entered
│  │  ─────────────────────────         │ │      twice)
│  │  ₦2,000,000 in cash                │ │
│  │  Purchased 8 July, 14:31           │ │
│  │  ✓ Paid entry                      │ │
│  └───────────────────────────────────┘ │
│                                         │
│                                         │  space.1200
│                                         │
│  ─────────────────────────────────      │
│                                         │
│  Enter this draw again  →               │  ← inline link, navy
│                                         │      returns to draw detail
│                                         │
│                                         │  bottom nav
├─────────────────────────────────────────┤
│  🏠 Draws    🎟 My tickets    👤 Me     │
└─────────────────────────────────────────┘
```

### 2.2 Layout — empty state (user has no tickets)

```
┌─────────────────────────────────────────┐
│                                         │
│  ← Back                                 │
│                                         │
│                                         │  space.800
│                                         │
│  My tickets                             │
│                                         │
│                                         │  space.2400
│                                         │
│          ┌──────────┐                   │  ← 80pt circle,
│          │    🎟    │                   │      surface.elevated,
│          └──────────┘                   │      gold ticket glyph inside
│                                         │
│                                         │  space.600
│                                         │
│         No tickets yet                  │  ← type.display.card, centered
│                                         │
│    This week's draw is open until       │  ← body.default, centered secondary
│    8pm Saturday.                        │
│                                         │
│                                         │  space.800
│                                         │
│  ┌───────────────────────────────────┐ │
│  │           See the draw             │ │  ← primary button
│  └───────────────────────────────────┘ │
│                                         │
└─────────────────────────────────────────┘
```

### 2.3 Components used

- `TopBar` — back + secondary "Refresh" action (V0.5 explicit refresh; V1 has real-time push).
- `SectionHeadline` — "My tickets".
- `SectionLabel` — gold group header ("Active — closes 8pm Saturday").
- `TicketCard` (list variant, 120pt tall) — the star of this wireframe. Spec below.
- `EmptyStateIllustration` — ticket glyph in circle.
- `Button` (primary) — empty state CTA.
- `InlineLink` — "Enter this draw again" (only appears if there IS a live draw AND user is not self-excluded).
- `BottomNav`.

### 2.4 States

**Default (tickets present, draw open):** as drawn in §2.1.

**Empty (no tickets):** as drawn in §2.2.

**Draw closed, awaiting reveal:** section label changes to *"Awaiting reveal — winner announced 9pm Sunday."* Ticket cards show a subtle *"Awaiting draw"* status chip in the corner (small, secondary, does not shout).

**Draw revealed — you didn't win:** section label *"Complete — draw was won by Ifeoma A. (Yaba)."* Ticket cards get a soft `surface.subtle` tint and a subtle *"Not this time."* line at the bottom. No sad language, no "better luck next time" (patronising). Just the fact.

**Draw revealed — you won:** the winning ticket card gets **special treatment** (see §2.5 winning-card variant). Other tickets from the same draw stay in the "not this time" state.

**Loading:** skeleton — 2 ticket-card placeholders shimmer.

**Error:** page-level banner + retry.

**Pull to refresh:** rubber-band; small `brand.accent` spinner at top.

### 2.5 The winning-ticket variant (post-reveal)

When the user has won, her winning ticket is *not* the same visual object as the others. It elevates:

- Card gets a full-width `color.brand.primary` (navy) top strip, 24pt tall, with the label *"Winning ticket"* in `type.label.micro` gold on navy.
- Ticket number typography stays the same size but colour switches to `color.text.accent` (gold — on the elevated warm surface, mono gold at 32pt sits at ~4:1 contrast — permitted for large text AA).
- A subtle emerald `✓ Winner` chip appears below the number.
- Bottom of card gains a *"See how to claim your prize"* row (primary variant, navy fill, `color.text.inverted`) — this is the *only* button anywhere on a ticket card. It appears only when the user has won.

The reason this matters: the winning ticket becomes the screenshot the user takes. It must look proud, be legible when compressed by WhatsApp, and carry the trust story (still shows the commitment hash link on the detail page). The card's identity as a *distinct object* holds under compression.

### 2.6 Copy

| Element | Copy |
|---|---|
| Page headline | My tickets |
| Section label (open) | Active — closes 8pm Saturday |
| Section label (closed, pre-reveal) | Awaiting reveal — winner announced 9pm Sunday |
| Section label (revealed, not won) | Complete — draw was won by {name} ({city}) |
| Section label (revealed, won) | You won this draw |
| Card top strip label (winning variant) | Winning ticket |
| Ticket sub-brand line | Atlas — Ticket |
| Ticket number | 04829 |
| Card meta 1 | ₦2,000,000 in cash |
| Card meta 2 | Purchased 8 July, 14:23 |
| Card meta 3 (paid) | ✓ Paid entry |
| Card meta 3 (free-route, when relevant) | ✓ Free-route entry |
| Card meta (not won) | Not this time. |
| Card meta (winning) | ✓ Winner |
| Enter again link | Enter this draw again → |
| Empty headline | No tickets yet |
| Empty body | This week's draw is open until 8pm Saturday. |
| Empty CTA | See the draw |
| Winning card CTA | See how to claim your prize |
| Error banner | We couldn't load your tickets. Pull to try again. |

**Copy commentary:**

- *"Not this time."* — deliberately not *"You didn't win"* (blunt) or *"Better luck next time"* (patronising, casino). *"Not this time."* is neutral fact plus an implication of *"there's a next time when you're ready."*
- The card sub-brand line *"Atlas — Ticket"* is present so a screenshotted ticket carries the brand attribution. It's small, in `type.label.micro`, but it means the ticket is unambiguously an Atlas artefact when it leaves the app.
- *"Enter this draw again"* — permitted because the mechanic allows multiple entries per user per draw. If we ever cap entries per user (V1 responsible-play consideration), this line disappears once the cap is reached.

### 2.7 Accessibility

- **Focus order:** Back → Refresh → Page headline → Section label (not focusable) → Ticket cards in order → "Enter again" link → BottomNav.
- **Ticket card as a11y group:** composite tap target (`role="link"` on web, `Semantics(button:true)` on Flutter). Screen-reader announces: *"Ticket zero four eight two nine. Two million naira in cash draw. Purchased 8 July, 14:23. Paid entry. Tap to view details."*
- **Winning ticket card:** announces first *"Winning ticket. Ticket zero four eight two nine..."* — the "Winning ticket" prefix is critical.
- **Refresh action:** small tap target concern — must be ≥ 44×44pt including padding around the label.
- **Contrast:** all pairings tokened. Winning card's gold-on-elevated-surface at 32pt passes AA large text.
- **Reduce motion:** ticket cards do not animate in on list load. Winning card no shine effect.

### 2.8 Interaction

- **Card tap:** navigates to Screen 5.2 (ticket detail) with a `Hero` animation on the ticket number — it flies from the card position to its enlarged position on the detail page. This is the signature interaction that says *"this ticket is a thing that persists across screens"*.
- **Winning card CTA tap:** navigates to Screen 7.1 (winner claim) — flagship step 7, wireframe 07 (Day 6).
- **Refresh:** re-fetches the ticket list. In V0.5, ticket data is authoritative from the backend; there's no offline queue.
- **Enter again link:** returns to draw detail (Screen 2.2) with the sticky Enter footer active.

---

## 3. Screen 5.2 — Ticket detail (the artefact)

### 3.1 Layout — active (draw open, awaiting close)

```
┌─────────────────────────────────────────┐
│                                         │
│  ← Back              Share ↗            │  ← top bar. Share = V0.5 stub toast
│                                         │
│                                         │  space.800
│                                         │
│                                         │  ─── FULL WIDTH TICKET ARTEFACT ───
│                                         │
│  ┌───────────────────────────────────┐ │  ← the artefact.
│  │                                    │ │      Full-bleed treatment.
│  │  ▪ ATLAS — TICKET                  │ │      radius.large, elevation.1,
│  │                                    │ │      surface.elevated, 32pt padding.
│  │                                    │ │
│  │                                    │ │      space.400
│  │                                    │ │
│  │  04829                             │ │  ← body.mono at 64pt (display size —
│  │                                    │ │      the ticket number IS the artefact)
│  │                                    │ │      color.text.primary
│  │                                    │ │
│  │  ═════════════════════════════     │ │  ← the "perforated" divider —
│  │                                    │ │      a dashed line in
│  │                                    │ │      color.divider.hairline
│  │                                    │ │      (visual reference: ticket stub)
│  │                                    │ │
│  │  This week's draw                  │ │  ← body.small, secondary uppercase
│  │  ₦2,000,000 IN CASH                │ │  ← body.emphasis, primary
│  │  Closes 8pm Saturday, 12 July      │ │  ← body.default, primary
│  │                                    │ │
│  │  ─────────────────────────         │ │  ← hairline
│  │                                    │ │
│  │  Purchased        8 July, 14:23    │ │  ← two-column: label + value,
│  │  Entry            Paid             │ │      body.default, primary
│  │  Reference        pi_5D7X…9B2     │ │      value column is body.mono for
│  │                                    │ │      the reference; label is regular
│  │                                    │ │
│  │  ─────────────────────────         │ │  ← hairline
│  │                                    │ │
│  │  Draw commitment                   │ │  ← body.small, secondary
│  │  3f2c…8a91  📋                     │ │  ← body.mono, 14pt, primary
│  │                                    │ │      copy-to-clipboard icon inline
│  │                                    │ │
│  └───────────────────────────────────┘ │
│                                         │
│                                         │  space.800
│                                         │
│  About this ticket                      │  ← type.display.card
│                                         │
│  Your entry is one of 1,247 in this     │  ← body.default
│  draw. All entries — paid and free      │
│  route — are drawn from the same pool.  │
│                                         │
│  When the draw closes, a public         │
│  entropy source picks the winner        │
│  from the pool. You'll see the result   │
│  as soon as it's announced.             │
│                                         │
│  See how the draw works  →              │  ← inline link, navy
│                                         │
│                                         │  space.800
│                                         │
│  ┌───────────────────────────────────┐ │
│  │    Enter this draw again           │ │  ← button, secondary variant
│  └───────────────────────────────────┘ │      (outline)
│                                         │
│                                         │  space.400
│                                         │
│  Remove this ticket                     │  ← inline link, subtle danger
│                                         │      only visible if refund window
│                                         │      is open (V0.5: never; refunds
│                                         │      are Day 8+ operator-initiated
│                                         │      per plan §3)
│                                         │
│                                         │  bottom safe area
└─────────────────────────────────────────┘
```

### 3.2 Layout — winning variant (post-reveal, user won)

```
┌─────────────────────────────────────────┐
│                                         │
│  ← Back              Share ↗            │
│                                         │
│                                         │  space.800
│                                         │
│  ┌───────────────────────────────────┐ │
│  │  ▪ WINNING TICKET                  │ │  ← navy strip at top of card,
│  │                                    │ │      32pt tall, brand.primary fill,
│  │                                    │ │      label in gold text.accent
│  │                                    │ │      (radius.large top-only)
│  ├───────────────────────────────────┤ │
│  │                                    │ │
│  │  ▪ ATLAS — TICKET                  │ │
│  │                                    │ │
│  │  04829                             │ │  ← body.mono at 64pt IN GOLD
│  │                                    │ │      (color.text.accent — earned by
│  │                                    │ │       the elevated card contrast)
│  │                                    │ │
│  │  ═════════════════════════════     │ │
│  │                                    │ │
│  │  ✓  Winner — ₦2,000,000 in cash    │ │  ← body.emphasis, state.success
│  │                                    │ │
│  │  Announced 9pm Sunday              │ │  ← body.small, secondary
│  │                                    │ │
│  │  ─────────────────────────         │ │
│  │                                    │ │
│  │  Purchased        8 July, 14:23    │ │
│  │  Entry            Paid             │
│  │  Reference        pi_5D7X…9B2     │
│  │                                    │
│  │  ─────────────────────────         │
│  │                                    │
│  │  Draw commitment                   │
│  │  3f2c…8a91  📋                     │
│  │                                    │
│  │  Revealed seed                     │  ← extra section only on winning card
│  │  9e01…4c67  📋                     │      shows the reveal proof inline
│  │                                    │
│  └───────────────────────────────────┘ │
│                                         │
│                                         │  space.800
│                                         │
│  ┌───────────────────────────────────┐ │
│  │       Claim your prize             │ │  ← primary button, navy fill
│  └───────────────────────────────────┘ │
│                                         │
│                                         │  space.400
│                                         │
│  See how this draw was verified  →      │  ← inline link, navy
│                                         │
└─────────────────────────────────────────┘
```

### 3.3 Layout — not-won variant (post-reveal)

Same as active variant (§3.1) with these changes:
- Header of the card includes a subtle line *"Not this time."* directly below the ticket number, in `body.small` secondary.
- The "About this ticket" section adds a final sentence: *"The winning ticket in this draw was 08114 — see how it was verified →"* (link to proof page).
- "Enter this draw again" button is hidden (draw is over).
- Primary CTA becomes *"See the current draw"* if there's a new active draw, otherwise omitted.

### 3.4 Components used

- `TopBar` (back + share stub).
- `TicketArtefact` — new *hero* component, only used on this screen. Composition:
  - `TicketBrandLine` (Atlas — Ticket, label.micro)
  - `TicketNumber` (mono 64pt)
  - `PerforatedDivider` (new — a dashed hairline that reads as ticket-stub perforation; purely aesthetic, does not indicate a tear or action)
  - `PrizeSummary` (draw name + amount + close time)
  - `MetaGrid` (2-column label/value)
  - `HashRow` (small mono + copy)
  - Winning-variant adds: `WinningStrip` (top), `WinnerLine` (success chip + line), `RevealedSeedRow` (second hash row)
- `SectionHeadline` — "About this ticket".
- `Button` (secondary for "Enter again"; primary for "Claim your prize" on winning variant).
- `InlineLink` — "See how the draw works", "Remove this ticket" (danger), "See how this draw was verified".

### 3.5 States

**Active (draw open):** as drawn in §3.1.

**Awaiting reveal (draw closed, pre-reveal):**
- *"Enter this draw again"* button hidden.
- Below-card line added: *"Sales closed 8pm Saturday. Winner announced 9pm Sunday."*
- Card is otherwise identical.

**Won:** §3.2 layout.

**Not won:** §3.3 layout.

**Loading:** skeleton of the artefact — number placeholder shimmer, meta rows shimmer. First load < 500ms.

**Error:** page-level banner + retry, no skeleton persisting.

### 3.6 Copy

| Element | Copy |
|---|---|
| Sub-brand | ATLAS — TICKET |
| Ticket number | 04829 |
| Prize summary label | This week's draw |
| Prize summary amount | ₦2,000,000 IN CASH |
| Prize summary close | Closes 8pm Saturday, 12 July |
| Meta: Purchased | Purchased / 8 July, 14:23 |
| Meta: Entry | Entry / Paid  (or  Entry / Free route) |
| Meta: Reference | Reference / pi_5D7X…9B2 |
| Commitment label | Draw commitment |
| Commitment value | 3f2c…8a91 |
| Winning strip | WINNING TICKET |
| Winner line | ✓ Winner — ₦2,000,000 in cash |
| Winner announced | Announced 9pm Sunday |
| Revealed seed label | Revealed seed |
| About headline | About this ticket |
| About body 1 | Your entry is one of 1,247 in this draw. All entries — paid and free route — are drawn from the same pool. |
| About body 2 | When the draw closes, a public entropy source picks the winner from the pool. You'll see the result as soon as it's announced. |
| Draw-works link | See how the draw works → |
| Enter again CTA | Enter this draw again |
| Refund link | Remove this ticket |
| Winning CTA | Claim your prize |
| Verified link | See how this draw was verified → |
| Not-won inline | Not this time. |
| Not-won trailing | The winning ticket in this draw was {number} — see how it was verified → |
| Share stub toast | Sharing arrives with V1. Copy the ticket link if you want to send it now. |
| Copy hash toast | Commitment hash copied. |
| Copy seed toast | Revealed seed copied. |
| Copy reference toast | Payment reference copied. |

**Copy commentary:**

- *"ATLAS — TICKET"* in uppercase label.micro — reads as "engraved" rather than "printed". The all-caps + tracking treatment makes the sub-brand feel like an imprint on a physical artefact. This is one of the very few uppercase strings in the product; earned by the artefact context.
- *"₦2,000,000 IN CASH"* also uppercase — for the ticket-artefact context only. On the draw detail page (wireframe 02), the same amount is title case. Uppercase here reads as "stamped".
- The reference (`pi_5D7X…9B2`) is Paystack's transaction ID (truncated for display, full on copy). Its presence on the ticket is a small but powerful trust cue — the ticket references a *real payment record*, not just a database row.
- *"See how the draw works"* is present even on an active ticket — the trust story doesn't wait until reveal.

### 3.7 Accessibility

- **Focus order:** Back → Share → Card (composite; but the copy-icons for hash / seed / reference are individually focusable within the card) → About section (heading, then paragraphs) → Primary CTA → Secondary link(s).
- **Card as composite:** the artefact reads top-to-bottom in one AT pass. *"Atlas ticket. Ticket number zero four eight two nine. This week's draw, two million naira in cash, closes 8pm Saturday, 12 July. Purchased 8 July, 14:23. Entry paid. Reference pi underscore 5 D 7 X truncated 9 B 2. Draw commitment hash, 3 f 2 c truncated 8 a 9 1, copy button."*
- **Copy icons:** each has explicit `aria-label` — *"Copy commitment hash"*, *"Copy revealed seed"*, *"Copy payment reference"*.
- **Winning variant:** the "WINNING TICKET" strip is announced first before the standard readout — this is the celebration moment for a screen-reader user.
- **Contrast:**
  - Standard variant: mono 64pt on `surface.elevated` = 15.3:1 ✅ AAA.
  - Winning variant gold ticket number on `surface.elevated`: 3.9:1 — passes AA large text (mono 64pt is well over the 24pt threshold). Documenting explicitly because gold typography on light surfaces is normally forbidden by tokens.md — this is the ONE exception, permitted only for the winning ticket number at ≥ 32pt.
- **Perforated divider:** aria-hidden (decorative).
- **Reduce motion:** Hero animation from card to detail becomes a fade. Winning variant's navy top strip appears solid, no slide-in.

### 3.8 Interaction

- **Copy hash / seed / reference:** copies full string to clipboard; toast per §3.6 copy table.
- **Enter again button:** returns to draw detail.
- **Claim your prize (winning only):** navigates to Winner Claim (wireframe 07, flagship step 7, Day 6).
- **See how this draw was verified:** navigates to public proof page (wireframe 12, Day 11).
- **Share stub:** toast per copy table; no share sheet in V0.5.
- **Remove this ticket:** hidden in V0.5. Design present because the placeholder disables in a systematic way (feature flag) rather than being absent from the codebase.

---

## 4. Design invariants for the ticket artefact

The following must hold across all variants and future iterations. Recording as invariants because this is the component most likely to get "improved" into blandness:

1. **The ticket number is the largest text on the page.** No other element out-sizes it. If a variant introduces a bigger element, the artefact is broken.
2. **The perforated divider is always present.** It's what makes this a ticket, not a card. Non-negotiable visual cue.
3. **The card has exactly one CTA button visible at a time.** The active state has *"Enter this draw again"* (secondary), the winning state has *"Claim your prize"* (primary). Never both, never zero (unless the state is closed-and-not-won-and-no-new-draw).
4. **The hash rows use `body.mono` (JetBrains Mono).** Never render a hash in any other font. This is the same visual language as the draw detail and the proof page — the ticket is a node in the same trust graph.
5. **The card renders identically in a screenshot as on the screen.** No live-tickers, no animations that would be missing from a static capture. The artefact must survive being a WhatsApp share.
6. **No promotional content on the ticket artefact.** No "Refer a friend" chip, no "Share for a bonus entry" (which V1 might introduce elsewhere but never *on* the ticket). The ticket is a possession, not a growth surface.

---

## 5. Open questions for founder review

1. **Perforated divider treatment.** Currently a `dashed line` in hairline colour. Alternatives: a series of small circles cut out of the card (semi-circular notches at both edges — reads more literally as ticket-stub); or a subtle repeating gold sawtooth. Recommend the dashed line — the notches are gimmicky, the sawtooth reads as decorative. Push back if the dashed feels too subtle.
2. **Ticket number size on artefact — 64pt.** This is deliberately huge. If it feels overweight in device testing, drop to 48pt. Recommend 64pt — the size *is* the affection.
3. **Sub-brand line *"ATLAS — TICKET"*** — the em-dash is intentional. Alternative: *"ATLAS TICKET"* (no dash), *"ATLAS · TICKET"* (middle dot). Recommend the em-dash — it reads as an inscription, not a label.
4. **Gold ticket number on winning ticket** — this is the *only* place gold typography appears on a light surface in the product. It's earned by the moment. If you want to keep the gold-on-light exception even tighter, the alternative is to keep the winning ticket number in `text.primary` (charcoal) and use gold *only* on the "WINNING TICKET" strip and the `✓ Winner` line. Recommend keeping gold on the number — this IS the screenshot moment.
5. **Uppercase ticket meta on artefact (*"₦2,000,000 IN CASH"*)** — the ticket-artefact context is the only place uppercase amounts appear. Alternative: keep title case throughout for consistency. Recommend the uppercase — it's the "stamped" texture that separates the artefact from every other card.
6. **"Not this time." — the not-won line.** Any pushback on this phrasing? I'm confident but flag if the tone feels off — this is a delicate copy moment.

---

## 6. Cross-references

- Flow source: `v0.5-demo-plan.md §2` (step 5).
- Upstream: `04-buy-ticket-skill-payment.md §5` (See-your-tickets CTA).
- Downstream (winning): `07-winner-claim.md` (Day 6, not yet drafted).
- Downstream (verification): `12-public-proof-page.md` (Day 11, not yet drafted).
- Anchor 3: `tone-doc.md §2 Anchor 3` (Range Rover configurator — the object-of-affection posture that this whole screen realises).
- Tokens: `tokens.md` — mono for ticket numbers and hashes, gold exception for winning-ticket typography, elevation.1 for the artefact card, radius.large.

---

🎨 *End of wireframe 05, and end of Day 5.*

*Day 5 completed: wireframes 04 (buy paid ticket) and 05 (my tickets — the Anchor 3 moment). Day 6 tomorrow: draw completes → notification → winner claim start (flagship steps 6–7, wireframes 06–07).*

*Six days into a two-week design pass; on schedule. Half of the consumer surface is now drafted. Push back on anything in 04 or 05 before Day 6 begins — post-Day-6 rework starts to cascade into Amelia's Week 3 backend contract assumptions.*

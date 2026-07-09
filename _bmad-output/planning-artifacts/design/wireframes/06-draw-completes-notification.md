# Wireframe 06 — Draw Completes → Notification

**Drafted:** 2026-07-08 (Day 6 per `tone-doc.md §8`)
**Amended:** 2026-07-08 (Day 7 per `tone-doc.md §8`) — winning-route disclosure removed from the reveal-page prose (§3.5); entry-count paid/free split retained everywhere. Per `docs/compliance/reviews/REVIEW-001` §2.3 (Adaeze). Winner-name publication (§2.6, §5) is now conditional on an explicit opt-in checkbox added at wf-07 §7.5; the anonymous variant of the reveal page (*"Winner — {city}"*) is flagged as a V1 design task in §7 below.
**Drafted by:** 🎨 Sally (BMad UX Designer)
**Status:** Draft — Adaeze approved with conditions on 2026-07-08 (REVIEW-001). For V0.5 investor demo scope the seeded winner is used and consent is not at issue; **winner-name publication is a hard blocker for real-user launch** without the opt-in checkbox landing on wf-07 §7.5 AND the anonymous reveal variant being designed.
**Covers:** Flagship flow step 6 from `v0.5-demo-plan.md §2` — *"Draw completes — user sees notification (in-app + Mailhog email) whether they won."*
**Surface:** Flutter consumer app (in-app surfaces) + email (Mailhog in V0.5 per plan §4).
**Pairs with:** `05-my-tickets.md` (draw states already covered there for the ticket-detail surface), `07-winner-claim-start.md` (the next screen for a winner), `tokens.md`, `tone-doc.md`, `docs/compliance/reviews/REVIEW-001-v0.5-consumer-wireframes.md`.

---

## 0. Why this moment matters

This is when the story either lands or doesn't.

The user has registered, browsed, taken a skill question, paid, and held a ticket for hours or days. In this moment, one of two things is true — she won, or she didn't. The product has to handle *both* outcomes with the same care. Losing is not a footnote. Losing well is a bigger design ask than winning well, because losing is the norm and winning is the exception; the average user's Atlas experience *is* being told they didn't win.

**Design goals for both variants:**
- The user finds out on the channel she was expecting to find out on (in-app + email).
- The message is unambiguous within 3 seconds of opening.
- The trust story continues — the notification links to the proof, so *"how do I know?"* has an answer immediately.
- No hedging language, no fake celebration, no fake commiseration.

**Non-goals for V0.5:**
- Push notifications (native OS). V1 — requires push infrastructure not in scope for Docker Compose demo. V0.5 uses in-app-on-launch delivery only (documented in plan §3).
- WhatsApp notifications. V1 per plan §3.
- SMS notifications (beyond OTP). V1.
- Real winner story-capture flow. V1.
- Consent-managed notification preferences (per-channel opt-in/out). V1 — V0.5 assumes all users are opted-in to email; no unsubscribe surface built.

---

## 1. Notification surfaces in V0.5

```
                    ┌──────────────────────────────────┐
                    │  Draw reveal event (server)      │
                    │  → outbox writes 2 messages:     │
                    └────────┬─────────────────────────┘
                             │
                ┌────────────┴──────────────┐
                │                           │
                ▼                           ▼
        ┌──────────────┐            ┌──────────────┐
        │  Email       │            │  In-app      │
        │  (Mailhog)   │            │  banner on   │
        │              │            │  next launch │
        │  templates   │            │              │
        │  6E.a / 6E.b │            │  screen 6.1  │
        └──────┬───────┘            └──────┬───────┘
               │                           │
               │                           ▼
               │                    ┌──────────────┐
               │                    │  Screen 6.2  │
               │                    │  In-app      │
               │                    │  notification│
               │                    │  detail /    │
               │                    │  reveal page │
               │                    └──────┬───────┘
               │                           │
               │                           ▼
               │                    ┌──────────────┐
               │                    │  Screen 6.3  │
               │                    │  Notification│
               │                    │  center      │
               │                    │  (history)   │
               │                    └──────────────┘
               │                           │
               ▼                           ▼
        (email opens         (winning → wireframe 07 claim
         a deep-link          non-winning → wireframe 05 ticket
         back into app)        detail)
```

Three in-app screens (6.1 banner, 6.2 detail/reveal, 6.3 notification center) + two email templates (6E.a winner, 6E.b non-winner). The reveal page (6.2) is the trust-story pivot for both variants.

---

## 2. Screen 6.1 — In-app banner on launch

The user opens the app after the draw has revealed. First thing she sees, above the home surface (screen 2.1), is a banner.

### 2.1 Layout — winner variant

```
┌─────────────────────────────────────────┐
│                                         │
│  Atlas              👤 Ifeoma  ▾        │  ← standard app bar
├─────────────────────────────────────────┤
│                                         │
│  ┌───────────────────────────────────┐ │  ← Banner, radius.large
│  │                                    │ │      surface: brand.primary (navy)
│  │  ▪ THIS WEEK'S DRAW                │ │      elevation.1
│  │                                    │ │      24pt padding
│  │                                    │ │      Full-width minus 16pt margins
│  │  You won ₦2,000,000.               │ │  ← type.display.card (24pt Fraunces)
│  │                                    │ │      color.text.accent (gold)
│  │                                    │ │
│  │  ────────────────────────          │ │  ← hairline in gold-tint dim
│  │                                    │ │
│  │  Announced 9pm Sunday.             │ │  ← body.default
│  │  Here's what happens next  →       │ │      color.text.inverted
│  │                                    │ │
│  └───────────────────────────────────┘ │
│                                         │
│                                         │  space.800
│                                         │
│  (rest of home surface below —          │
│   screen 2.1 content in the             │
│   post-reveal state per §2.3 of         │
│   wireframe 02)                         │
│                                         │
└─────────────────────────────────────────┘
```

### 2.2 Layout — non-winner variant

```
┌─────────────────────────────────────────┐
│                                         │
│  Atlas              👤 Chinelo  ▾        │
├─────────────────────────────────────────┤
│                                         │
│  ┌───────────────────────────────────┐ │  ← Banner, radius.large
│  │                                    │ │      surface: surface.elevated
│  │  ▪ THIS WEEK'S DRAW                │ │      elevation.1
│  │                                    │ │      24pt padding
│  │                                    │ │
│  │  Not this time. The winner was     │ │  ← type.body.emphasis, primary
│  │  Ifeoma A. (Yaba).                 │ │      (body.emphasis rather than display
│  │                                    │ │       — this moment is smaller than
│  │                                    │ │       the winning moment, on purpose)
│  │  ────────────────────────          │ │
│  │                                    │ │
│  │  See how the draw was verified →   │ │  ← inline link, navy
│  │                                    │ │      body.default
│  │                                    │ │
│  └───────────────────────────────────┘ │
│                                         │
└─────────────────────────────────────────┘
```

### 2.3 Layout — did-not-enter-this-draw variant (edge case)

If the user is logged in but did not enter this draw (unlikely in V0.5 with single seed draw, but designed for robustness): no banner. Home surface shows the draw in its post-reveal state per wireframe 02 §2.3.

### 2.4 Components used

- `NotificationBanner` — new; two variants (celebrated = navy fill + gold text, standard = surface.elevated + primary text). Full-width minus 16pt page margins. Dismissable via X in the top-right corner — but explicitly *not* auto-dismissing.
- `InlineLink` — trailing "Here's what happens next" (winner) / "See how the draw was verified" (non-winner).

### 2.5 States

**Winner (unclaimed):** as drawn in §2.1. Tap → screen 6.2 (reveal page) OR direct to claim flow (wireframe 07) — see interaction notes.

**Winner (claim already started/completed):** banner suppressed. User has already been through the winning-claim moment; on subsequent launches, home surface shows the closed-draw state and the ticket appears in My tickets as a winning ticket.

**Non-winner:** as drawn in §2.2. Tap → screen 6.2 (reveal page).

**Non-participant (edge):** no banner (§2.3).

**Banner dismissed:** returns to a subtle chip in the top of the home surface: *"You won — here's what happens next →"* / *"See how the draw was verified →"*. Chip persists until the winner claims OR the next draw goes live.

**Loading (banner data not yet fetched on cold launch):** banner does NOT appear as skeleton. It appears only when data is confirmed — a shimmer where the banner will be would be misleading (implying pending news).

### 2.6 Copy

| Element | Copy |
|---|---|
| Eyebrow (both) | THIS WEEK'S DRAW |
| Winner headline | You won ₦{amount}. |
| Winner sub-line | Announced {day} {time}. |
| Winner CTA | Here's what happens next → |
| Non-winner headline | Not this time. The winner was {name} ({city}). |
| Non-winner CTA | See how the draw was verified → |
| Winner chip (dismissed) | You won — here's what happens next → |
| Non-winner chip (dismissed) | See how the draw was verified → |

**Copy commentary:**

- *"You won ₦2,000,000."* — the amount comes first, in gold. This is the sentence she screenshots. No preamble ("Congratulations!"), no wrap-up ("You're a winner!") — just the fact, in the largest gold on the screen.
- *"Here's what happens next"* on the winning CTA — a promise of guidance, not another celebration. This is the moment she needs to know *what to do*, not to be told again that she won.
- Non-winner reuses *"Not this time."* from the ticket detail (wireframe 05 §3.6). Ritual repetition. Same phrase, same posture, wherever losing is announced.
- Winner name + city on the non-winner variant. This is a trust move — the winner is *specific*, not abstract. It signals *someone real won*, and helps establish the reveal as authentic, not TV-lottery-abstract.

### 2.7 Accessibility

- **Announcement on mount:** banner reads via `aria-live="assertive"` on cold-launch — *"You won two million naira. Announced 9pm Sunday. Here's what happens next, opens details."* For non-winner: *"Not this time. The winner was Ifeoma A, Yaba. See how the draw was verified, opens details."*
- **Focus order:** app bar wordmark → greeting chip → banner (composite tap target) → banner CTA (individually focusable within the composite) → rest of home surface.
- **Dismiss X:** ≥ 44pt tap area; `aria-label="Dismiss"`.
- **Contrast:**
  - Winner variant: gold headline on navy = 7.2:1 ✅. Body text inverted on navy = 14.8:1 ✅.
  - Non-winner: text.primary on surface.elevated = 15.3:1 ✅.
- **Reduce motion:** banner appears solid (no slide-in). Dismiss = instant, no fade.

### 2.8 Interaction

- **Tap banner body (winner):** navigates to screen 6.2 (reveal page). The reveal page is the *reveal experience* — a moment to see the outcome in context, before proceeding to claim.
- **Tap banner body (non-winner):** navigates to screen 6.2 (reveal page).
- **Tap CTA (winner):** shortcut — bypasses reveal page, goes directly to wireframe 07 claim. This is a deliberate two-path design: the banner body invites her to *see* the reveal; the CTA lets her *act* on it. Different users at different moments will want different things; two paths honour both.
- **Dismiss:** banner collapses to a persistent chip; chip persists until claim started or next draw goes live.
- **Deep-link from email:** email deep-links directly to screen 6.2 with a "just opened from email" query param that suppresses the banner (avoids double-notification feel).

---

## 3. Screen 6.2 — Reveal page

This is the trust-story pivot. Whether the user won or lost, this is the page that answers *"how do I know?"*

### 3.1 Layout — winner variant

```
┌─────────────────────────────────────────┐
│                                         │
│  ← Back              🔗 Share ↗          │  ← top bar
│                                         │
│                                         │  space.800
│                                         │
│  ▪ THIS WEEK'S DRAW — COMPLETE           │  ← type.label.micro gold uppercase
│                                         │
│                                         │  space.300
│                                         │
│  You won ₦2,000,000.                    │  ← type.display.hero (64pt Fraunces)
│                                         │      color.text.primary
│  in cash                                │  ← body.default, secondary
│                                         │
│                                         │  space.800
│                                         │
│  ─────────────────────────────          │  ← hairline
│                                         │
│  Ticket 04829                           │  ← body.mono 24pt, primary
│  ✓ Winner                               │  ← body.default, state.success
│                                         │
│                                         │  space.400
│                                         │
│  Purchased 8 July, 14:23                │  ← body.small, secondary
│  Entry: Paid                            │
│                                         │
│                                         │  space.800
│                                         │
│  ─────────────────────────────          │  ← hairline
│                                         │
│  How the winner was chosen              │  ← type.display.card
│                                         │
│                                         │  space.400
│                                         │
│  1,247 entries were in this draw.       │  ← body.default
│  1,160 paid. 87 via the free route.     │
│  All were drawn from the same pool.     │
│                                         │
│                                         │  space.400
│                                         │
│  A public entropy source — Bitcoin      │
│  block #856,142 and drand round         │
│  #4,829,301 — determined the winning    │
│  ticket. The proof is verifiable.       │
│                                         │
│                                         │  space.600
│                                         │
│  ┌───────────────────────────────────┐ │
│  │  ▪ VERIFIED                        │ │  ← ProofSummaryCard
│  │                                    │ │      radius.large, surface.elevated
│  │  Commitment    3f2c…8a91           │ │      elevation.0
│  │  Revealed seed 9e01…4c67           │ │      body.mono 14pt
│  │  Winner ticket 04829               │ │      3 rows, hairline dividers
│  │                                    │ │
│  │  See full proof →                  │ │  ← inline link, navy
│  │                                    │ │
│  └───────────────────────────────────┘ │
│                                         │
│                                         │  space.800
│                                         │
│  ┌───────────────────────────────────┐ │
│  │      Claim your prize              │ │  ← primary button (navy fill)
│  └───────────────────────────────────┘ │
│                                         │
│                                         │  space.400
│                                         │
│  Back to Atlas                          │  ← inline link, secondary centered
│                                         │
└─────────────────────────────────────────┘
```

### 3.2 Layout — non-winner variant

```
┌─────────────────────────────────────────┐
│                                         │
│  ← Back              🔗 Share ↗          │
│                                         │
│                                         │  space.800
│                                         │
│  ▪ THIS WEEK'S DRAW — COMPLETE           │
│                                         │
│                                         │  space.300
│                                         │
│  Won by Ifeoma A. (Yaba)                │  ← type.display.section (40pt Fraunces)
│                                         │      color.text.primary
│                                         │      (smaller than winner variant —
│                                         │       the moment is smaller)
│                                         │
│                                         │  space.400
│                                         │
│  ₦2,000,000 in cash                     │  ← body.default, secondary
│                                         │
│                                         │  space.800
│                                         │
│  ─────────────────────────────          │
│                                         │
│  Your ticket                            │  ← body.small, secondary uppercase
│                                         │
│  Ticket 04829                           │  ← body.mono 24pt, primary
│  Not this time.                         │  ← body.default, secondary
│                                         │      (NOT state.danger — this is not
│                                         │       an error, it's an outcome)
│                                         │
│                                         │  space.800
│                                         │
│  ─────────────────────────────          │
│                                         │
│  How the winner was chosen              │
│                                         │
│  (identical prose + ProofSummaryCard    │
│   as winner variant — see §3.1)         │
│                                         │
│                                         │  space.800
│                                         │
│  ┌───────────────────────────────────┐ │
│  │        See the current draw        │ │  ← button, secondary variant
│  └───────────────────────────────────┘ │      (only if there IS a current draw
│                                         │       — otherwise omitted)
│                                         │
│                                         │  space.400
│                                         │
│  Back to Atlas                          │  ← inline link, secondary centered
│                                         │
└─────────────────────────────────────────┘
```

### 3.3 Components used

- `TopBar` (back + share stub).
- `SectionLabel` (gold eyebrow).
- `PrizeAmount` (hero for winner, section for non-winner).
- `TicketReferenceRow` — small composition: ticket number in mono + outcome line + purchase metadata.
- `SectionHeadline` — "How the winner was chosen".
- `ProofSummaryCard` — new. 3 hash-style rows (commitment, revealed seed, winner ticket) + "See full proof" link.
- `Button` (primary for winner "Claim your prize"; secondary for non-winner "See the current draw").
- `InlineLink` (Back to Atlas).

### 3.4 States

**Winner (unclaimed):** as drawn §3.1.
**Winner (claim in progress):** primary CTA changes to *"Continue your claim"*.
**Winner (claim submitted, awaiting review):** primary CTA becomes *"See claim status"* (opens screen 7.4).
**Winner (claim complete, payment sent):** primary CTA becomes *"See how the payment was made"* — links to ticket detail winning variant showing the ledger reference.

**Non-winner:** as drawn §3.2.
**Non-participant:** page shows a shortened variant — no "Your ticket" section, just the announcement + how-the-winner-was-chosen block. Reachable from a public link.

**Loading (rare — reveal page is fetched fresh on entry):** skeleton for the amount, ticket line, and proof card.

**Error:** page-level banner + retry.

### 3.5 Copy

| Element | Copy |
|---|---|
| Eyebrow | THIS WEEK'S DRAW — COMPLETE |
| Winner headline | You won ₦{amount}. |
| Non-winner headline | Won by {name} ({city}) |
| Prize unit | in cash |
| Ticket header (non-winner) | Your ticket |
| Ticket outcome (winner) | ✓ Winner |
| Ticket outcome (non-winner) | Not this time. |
| Purchase meta | Purchased {date}, {time} / Entry: {Paid or Free route} |
| How-winner-chosen headline | How the winner was chosen |
| How-winner-chosen para 1 | 1,247 entries were in this draw. 1,160 paid. 87 via the free route. All were drawn from the same pool. |
| How-winner-chosen para 2 | A public entropy source — Bitcoin block #{n} and drand round #{n} — determined the winning ticket. The proof is verifiable. |
| Proof card eyebrow | VERIFIED |
| Proof card rows | Commitment / Revealed seed / Winner ticket |
| Full-proof link | See full proof → |
| Winner CTA | Claim your prize |
| Winner CTA (in progress) | Continue your claim |
| Winner CTA (submitted) | See claim status |
| Non-winner CTA | See the current draw |
| Back link | Back to Atlas |

**Copy commentary:**

- The entry-count split (`1,160 paid. 87 via the free route.`) lands here as public draw-composition data, followed by the operational commitment (*"All were drawn from the same pool"*). **This copy is retained per REVIEW-001 §2.3.** What is *not* here — and must not be introduced in V0.5 — is a per-draw *"the winning ticket came from the paid/free route"* line. Adaeze held that disclosure for V1 pending counsel; adverse-selection appearance risk on small samples and winner-identifiability risk in small free-route pools were the reasons.
- *"The proof is verifiable."* is not marketing — it is a factual promise that the ProofSummaryCard and the full proof page (Day 11) honour. Trust-story language should always be redeemable.
- Non-winner primary text uses *"Not this time."* (again) — reinforcing the anchor phrase from wireframe 05 and the banner in 6.1.
- **Winner name displays** on the non-winner banner (§2.2), non-winner reveal (§3.2), non-winner email (§5.2), and notification-centre non-participant row (§4.4) all depend on the winner having ticked the opt-in publication consent added at wf-07 §7.5 (per REVIEW-001 §4.3 + §5.5 + §5.8). When consent is declined, all winner-name placements fall back to *"Winner — {city}"* — the anonymous variant. **Design of the anonymous variant across every surface listed above is a V1 pre-launch task** and is added to §7 below.

### 3.6 Accessibility

- **Focus order:** Back → Share → Page headline (announced) → Ticket reference row → How-winner-chosen headline + paragraphs → Proof card (composite; individual hash rows have copy affordances not shown in ASCII but implemented per wireframe 05 hash-row pattern) → Primary CTA → Back link.
- **Winner page announcement on mount:** *"This week's draw is complete. You won two million naira in cash. Ticket zero four eight two nine, winner."* — the celebration is in the announcement, not in redundant confetti sound effects.
- **Non-winner announcement on mount:** *"This week's draw is complete. Won by Ifeoma A, Yaba. Two million naira in cash. Your ticket, zero four eight two nine. Not this time."*
- **Proof card copy icons:** individually focusable and labelled as in wireframe 05 §3.7.
- **Contrast:** all tokens as spec.

### 3.7 Interaction

- **Claim your prize:** navigates to wireframe 07 §2 (claim intro).
- **See full proof:** navigates to wireframe 12 (public proof page, Day 11).
- **See the current draw:** navigates to draw detail (screen 2.2) of the *next* active draw. Hidden if none exists.
- **Share (stub):** toast per prior wireframes.
- **Share (V1 note):** for the winner variant, share will pre-compose *"I entered the Atlas draw and won ₦2,000,000. The result is publicly verifiable at {url}"*. This copy is drafted here as a marker for V1 to inherit; not shipped in V0.5.

---

## 4. Screen 6.3 — Notification center (history)

Accessed from the greeting-chip overflow menu (screen 2.1) → *"Notifications"*.

### 4.1 Layout

```
┌─────────────────────────────────────────┐
│                                         │
│  ← Back              Mark all read      │  ← top bar
│                                         │
│                                         │  space.600
│                                         │
│  Notifications                          │  ← type.display.section
│                                         │
│                                         │  space.400
│                                         │
│  ▪ TODAY                                 │  ← section label, gold uppercase
│                                         │
│  ┌───────────────────────────────────┐ │  ← NotificationRow, unread
│  │  ●  Draw complete                  │ │      leading dot = unread indicator
│  │     You won ₦2,000,000 —           │ │      in gold, 8pt
│  │     Ticket 04829                   │ │
│  │     9pm Sunday                     │ │  ← body.small secondary
│  └───────────────────────────────────┘ │
│                                         │  space.300
│  ┌───────────────────────────────────┐ │  ← NotificationRow, read
│  │     Ticket confirmed               │ │      no leading dot
│  │     Ticket 04829 — ₦2,000,000      │ │
│  │     draw. Good luck.               │ │
│  │     8 July, 14:23                  │ │
│  └───────────────────────────────────┘ │
│                                         │
│                                         │  space.600
│                                         │
│  ▪ EARLIER                              │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │     Welcome to Atlas               │ │
│  │     We're glad you're here.        │ │
│  │     3 July, 09:12                  │ │
│  └───────────────────────────────────┘ │
│                                         │
│                                         │  bottom safe area
└─────────────────────────────────────────┘

Empty state:
   "You have no notifications yet.
    We'll let you know when a draw closes."
```

### 4.2 Components

- `TopBar` (back + "Mark all read" trailing action).
- `SectionHeadline`.
- `SectionLabel` (Today / Earlier — gold uppercase).
- `NotificationRow` — new; leading unread dot (gold, 8pt) + headline + body + timestamp. Read state removes dot. Composite tap target.

### 4.3 States

**Default:** as drawn.

**All read:** no dots, "Mark all read" trailing action grays out.

**Empty:** centered illustration + copy per §4.1 note.

**Loading:** skeleton rows shimmer.

### 4.4 Copy

| Notification type | Headline | Body |
|---|---|---|
| Draw complete — winner | Draw complete | You won ₦{amount} — Ticket {number} |
| Draw complete — non-winner | Draw complete | Won by {name}. See how the draw was verified. |
| Draw complete — non-participant | Draw complete | ₦{amount} was won by {name} ({city}). See how. |
| Ticket confirmed | Ticket confirmed | Ticket {number} — ₦{amount} draw. Good luck. |
| Welcome | Welcome to Atlas | We're glad you're here. |
| Draw closing soon (opt-in, V1) | (deferred) | (deferred) |

### 4.5 Accessibility

- **Row semantics:** each row is a link with composite label combining headline + body + timestamp. Unread state announced first (*"Unread. Draw complete. You won two million naira..."*).
- **Mark all read:** confirmation via toast *"Marked all as read."*
- **Focus order:** Back → Mark all read → Section headline → rows in order.

### 4.6 Interaction

- **Row tap:** navigates per notification type. Draw-complete → screen 6.2. Ticket-confirmed → wireframe 05 §3 (ticket detail). Welcome → home.
- **Mark all read:** clears unread state client-side; syncs backend.
- **Long-press on row:** V0.5 no action. V1: *"Delete notification"*.

---

## 5. Email templates

Delivered via Mailhog in V0.5 per plan §4. Two template designs — winner (6E.a) and non-winner (6E.b). Ticket-confirmation email is a separate template (6E.c) triggered on successful payment (out of scope here — belongs conceptually to wireframe 04 but included below for completeness of the email surface).

Emails are HTML with a plain-text fallback. Widths: 600px max, mobile-responsive (single-column below 480px).

### 5.1 Template 6E.a — Winner email

```
Subject: You won the Atlas draw.
Preheader: Ticket 04829 — ₦2,000,000. Here's what happens next.

╔══════════════════════════════════════════════╗
║                                              ║
║   [Atlas wordmark, Fraunces 24pt gold]       ║
║                                              ║
╠══════════════════════════════════════════════╣
║                                              ║
║   THIS WEEK'S DRAW                           ║  ← label.micro gold
║                                              ║
║   You won ₦2,000,000.                        ║  ← display.section (32pt Fraunces)
║                                              ║      text.primary
║   ─────────────────────                      ║
║                                              ║
║   Ticket 04829                               ║  ← body.mono 20pt
║   Announced 9pm Sunday.                      ║  ← body.default secondary
║                                              ║
║   ─────────────────────                      ║
║                                              ║
║   The prize is ₦2,000,000 in cash, paid      ║  ← body.default
║   to a Nigerian bank account of your         ║
║   choice within 5 working days of your       ║
║   claim being received.                      ║
║                                              ║
║   To claim, open Atlas and follow the        ║
║   steps on your ticket page. You'll need:    ║
║                                              ║
║   • A bank account in your legal name        ║  ← bullet list, body.default
║   • Your BVN                                 ║
║   • A government-issued ID                   ║
║                                              ║
║   ─────────────────────                      ║
║                                              ║
║   [ Open Atlas to claim → ]                  ║  ← button — deep-link to app
║                                              ║      brand.primary fill, gold text
║                                              ║
║   ─────────────────────                      ║
║                                              ║
║   How the winner was chosen                  ║  ← display.card
║                                              ║
║   1,247 entries. 1,160 paid, 87 via free    ║  ← body.default
║   route. All drawn from the same pool. A     ║
║   public entropy source (Bitcoin block       ║
║   #856,142 + drand round #4,829,301)         ║
║   determined the winning ticket.             ║
║                                              ║
║   Verify it yourself:                        ║
║   {public proof URL}                         ║  ← body.mono, navy link
║                                              ║
║   ─────────────────────                      ║
║                                              ║
║   Questions? Reply to this email or          ║  ← body.small secondary
║   contact us on {support channel}.           ║
║                                              ║
║   ─────────────────────                      ║
║                                              ║
║   Atlas Africa Ltd — {address}               ║  ← body.small, secondary
║   You're receiving this because you          ║      footer with legal identifier
║   entered a draw at Atlas.                   ║
║                                              ║
║   [Unsubscribe — V1]                         ║      (V0.5: link stub)
║                                              ║
╚══════════════════════════════════════════════╝
```

### 5.2 Template 6E.b — Non-winner email

```
Subject: Atlas draw result — this week
Preheader: Won by Ifeoma A. (Yaba). See the proof.

╔══════════════════════════════════════════════╗
║                                              ║
║   [Atlas wordmark, Fraunces 24pt gold]       ║
║                                              ║
╠══════════════════════════════════════════════╣
║                                              ║
║   THIS WEEK'S DRAW — COMPLETE                ║  ← label.micro gold
║                                              ║
║   Won by Ifeoma A. (Yaba)                    ║  ← display.card (24pt Fraunces)
║   ₦2,000,000 in cash                         ║  ← body.default secondary
║                                              ║
║   ─────────────────────                      ║
║                                              ║
║   Your ticket                                ║  ← label.micro secondary
║   Ticket 04829 — Not this time.              ║  ← body.mono / body.default
║                                              ║
║   ─────────────────────                      ║
║                                              ║
║   How the winner was chosen                  ║  ← display.card
║                                              ║
║   1,247 entries. 1,160 paid, 87 via free    ║  ← body.default
║   route. All drawn from the same pool. A     ║
║   public entropy source (Bitcoin block       ║
║   #856,142 + drand round #4,829,301)         ║
║   determined the winning ticket.             ║
║                                              ║
║   Verify it yourself:                        ║
║   {public proof URL}                         ║  ← body.mono, navy link
║                                              ║
║   ─────────────────────                      ║
║                                              ║
║   [ See the current draw → ]                 ║  ← button (only if there IS one)
║                                              ║      surface.elevated, navy text,
║                                              ║      outline variant
║                                              ║
║   ─────────────────────                      ║
║                                              ║
║   Atlas Africa Ltd — {address}               ║
║   You're receiving this because you          ║
║   entered a draw at Atlas.                   ║
║                                              ║
║   [Unsubscribe — V1]                         ║
║                                              ║
╚══════════════════════════════════════════════╝
```

### 5.3 Template 6E.c — Ticket confirmed email (triggered from wireframe 04)

```
Subject: Ticket 04829 — Atlas
Preheader: You're in the ₦2,000,000 draw. Closes 8pm Saturday.

╔══════════════════════════════════════════════╗
║                                              ║
║   [Atlas wordmark]                           ║
║                                              ║
║   ─────────────────────                      ║
║                                              ║
║   TICKET CONFIRMED                           ║  ← label.micro gold
║                                              ║
║   Ticket 04829                               ║  ← body.mono 32pt
║                                              ║
║   ─────────────────────                      ║
║                                              ║
║   This week's draw                           ║
║   ₦2,000,000 in cash                         ║
║   Closes 8pm Saturday, 12 July               ║
║                                              ║
║   Payment reference   pi_5D7X…9B2            ║
║   Commitment hash     3f2c…8a91              ║
║                                              ║
║   ─────────────────────                      ║
║                                              ║
║   [ Open Atlas → ]                           ║
║                                              ║
╚══════════════════════════════════════════════╝
```

### 5.4 Email design invariants

Recording as invariants — email is the surface most likely to get "spammed up" over time:

1. **No promotional content in transactional emails.** No "You might also like…", no cross-sell, no upcoming-draw teaser. A transactional email is transactional.
2. **Wordmark only in header.** No hero banner image. Images can fail to load; the header must still work as text-only.
3. **Verify-yourself link is in every draw-complete email.** The trust story travels with the email.
4. **The email is legible with images off.** Every email client blocks images by default until the sender is whitelisted. Every element renders in text.
5. **Footer legal identity is present.** Company name, registered address. This is compliance-load-bearing.
6. **Unsubscribe.** V0.5 is a stub; V1 must have a functional unsubscribe. Ship-blocker for real-user launch.

### 5.5 Accessibility for email

- Semantic HTML (`<h1>`, `<h2>`, `<ul>`, `<p>`) — every email client's screen-reader path improves with real structure.
- All buttons are `<a>` styled as buttons (email clients don't support real `<button>`) with `role="button"` if supported.
- Alt text on the wordmark image: *"Atlas"*.
- Preheader text (the first 100 characters of the email body, shown by mail clients as preview) is carefully composed for every template — see subject/preheader lines above.
- No hover-dependent affordances (email is often print/read-only).

---

## 6. Design invariants for the notification surface

Preserving alongside the ticket artefact invariants (wireframe 05 §4):

1. **The user is always told, on the primary surface, whether she won or lost.** No case where the app hides the outcome behind another tap.
2. **Losing is not chrome.** The non-winner banner and reveal page get the same design attention as the winner variants.
3. **The proof is always one link away.** From banner, from reveal, from email — the *"verify it yourself"* path is available in every notification touchpoint.
4. **No urgency copy on the win.** No *"Claim within 24 hours!"*, no *"Act fast!"*. The claim window is real (V1 will have one), but urgency-marketing on a winning-outcome moment reads as manipulative. Copy should be calm even when the underlying deadline is real.
5. **Winner name + city always specific on non-winner surfaces.** Never anonymised. The winner is a real person; the abstraction of the winner is a lottery-marketing tell.

---

## 7. Open questions for founder + agents

### For founder:

1. **Non-winner banner headline uses `body.emphasis`, not display type** (§2.2). This deliberately makes losing "smaller" than winning. Any pushback? Alternative: use display.card for both variants, differentiate only by fill colour. Recommend the current tiered approach — the winning moment IS bigger, and pretending otherwise would feel forced.
2. **Two paths from winner banner** (banner body → reveal page; CTA → direct to claim) — is the split intentional-feeling or confusing? I'd hold — the reveal-page-first path is the *right* one for the trust story, but I don't want to force a user who is ready to claim to take an extra step.
3. **Winner name + city on non-winner banner + reveal page + email.** *"Ifeoma A. (Yaba)"* — first name + last initial + city. This assumes we have consent-to-publish from the winner. **Consent capture flow is a V1 gap** — for V0.5 demo, we seed a synthetic winner. Flag: production launch needs consent-capture step in the claim flow (wireframe 07 §5).
4. **Ticket-confirmed email (6E.c).** Do you want this to send in V0.5? It creates a second Mailhog message per purchase, which slightly clutters the demo. Recommend keep — the ticket-confirmed email is the trust proof for the *entry*, not just the reveal. It reinforces "Atlas emails you records of everything you do."
5. **Non-participant reveal page variant.** Anyone with the public URL can visit — a reveal-outcome page with the proof, but no personalised ticket section. Useful for the "share the result" moment (V1 shares this URL). Confirm this variant belongs in V0.5?

### For ⚖️ Adaeze — RESOLVED 2026-07-08 by REVIEW-001

6. **Prize claim requirements** — resolved §4.1: current three items (bank in legal name, BVN, gov ID) are the minimum and are approved. For real-user launch, **add** tax-status attestation and source-of-funds attestation for prizes above the founder-approval threshold (working position ₦5M per AINE-AGENTS.md §6). Wording pending counsel.
7. **"Claim within 5 working days" phrasing** — resolved §4.2: reads as Atlas's SLA for payout after a *completed* claim, which is the correct posture. Approved as-is. Any winner-side claim-window policy (must-claim-within-N-days) is a separate policy needing counsel and does not exist in V0.5.
8. **Winner-name publication ("Ifeoma A., Yaba")** — resolved §4.3: approved for V0.5 seeded winner only. **Real-user launch requires** explicit opt-in checkbox on wf-07 §7.5 (added in wf-07 amendment 2026-07-08) AND design of the anonymous *"Winner — {city}"* variant across every surface in §3.5 commentary above. Anonymous variant is a V1 pre-launch design task; adding to §7 below.
9. **Legal footer on emails** — resolved §4.4: current footer is **rejected for real-user launch** — needs company RC number, full registered office address, prize-competition licence reference (if any per counsel), data controller identity + DPO contact route, functional unsubscribe, and SPF/DKIM/DMARC on the sending domain. Current V0.5 footer is acceptable for Mailhog demo. All six items are Phase 3 blockers.
10. **"Verify it yourself" URL indexability** — resolved §4.5: approved with one technical accommodation — the public proof URL must be keyed by `draw_id`, not by winner, and the winner name (if consented) must not be part of the indexable HTML. Rendered client-side after page load OR omitted from the public page entirely and shown only to authenticated winners/participants. Recommend the latter. Amelia — Draw-Engine + public-web contract point; Adaeze will re-review this specifically when wf-12 (public proof page) drafts.

### For 💻 Amelia:

11. **Notification-on-launch delivery mechanism** — V0.5 uses "on-launch fetch" per plan §3 (no push infrastructure). API endpoint that returns unread notifications for the user. Confirm this fits the outbox model per ADR-002.
12. **Email template rendering** — recommend `Jinja2` templates on the FastAPI side, keyed by event type. Templates in `templates/email/`. Rendering is a subscription of the outbox worker.
13. **Deep-link scheme for email → app** — `atlas://reveal/{draw_id}?from=email` and `atlas://claim/{draw_id}?from=email`. Same scheme as wireframe 02.
14. **Ticket-confirmed email delivery timing** — should send AFTER `ticket_issued` event lands on outbox, not from within the payment webhook handler. This preserves the "email is a subscription of the audit-logged event, not a side-effect of a webhook" principle.

---

## 8. Cross-references

- Draw states also documented in: `02-browse-active-draw.md §2.3, §3.3` and `05-my-tickets.md §2.4`.
- Next screen (winner path): `07-winner-claim-start.md` (this Day 6 delivery, sibling file).
- Proof page (Day 11): `12-public-proof-page.md`.
- Tokens: `tokens.md`.
- Tone: `tone-doc.md` — non-winner language commitment (§5), warm-not-cold shadows on email cards (§4 no email shadow but same warmth principle).
- ADRs: ADR-002 outbox (notification delivery), ADR-005 audit log (each notification event is logged), ADR-006 commit-reveal (the reveal-source content).
- Plan: `v0.5-demo-plan.md §2` step 6, §3 (V0.5 exclusions — no push, no WhatsApp).

---

🎨 *End of wireframe 06. Continues with `07-winner-claim-start.md` — the claim flow. Once that lands Day 6 is complete and we're through the consumer flagship flow up to and including winner initiation.*

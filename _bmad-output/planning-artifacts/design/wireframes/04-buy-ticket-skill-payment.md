# Wireframe 04 — Buy Paid Ticket (Skill Question → Payment → Ticket Issued)

**Drafted:** 2026-07-08 (Day 5 per `tone-doc.md §8`)
**Amended:** 2026-07-08 (Day 7 per `tone-doc.md §8`) — skill-question intro rewritten to drop the first-person legal-classification claim (§2.4), applying the same substitution made on wf-03. Per `docs/compliance/reviews/REVIEW-001` §3.3 (Adaeze).
**Drafted by:** 🎨 Sally (BMad UX Designer)
**Status:** Draft — Adaeze approved with conditions on 2026-07-08 (REVIEW-001) for V0.5 demo scope; skill-question *difficulty* rejected for real-user launch (Phase 3 blocker — Adaeze owns the question-pool architecture at `docs/compliance/skill-questions.md`). Founder review pending Week 1 exit.
**Covers:** Flagship flow step 4 from `v0.5-demo-plan.md §2` — *"Buy paid ticket — click 'Enter' → skill question (multiple choice, rotated from seed pool) → correct answer → Paystack sandbox checkout → ticket appears in 'My tickets.'"*
**Surface:** Flutter consumer app, with a Paystack sandbox webview interlude.
**Pairs with:** `05-my-tickets.md` (the destination of a successful buy), `03-free-entry-disclosure.md` (skill question wording must align — same question, both routes), `tokens.md`, `tone-doc.md`, `docs/compliance/reviews/REVIEW-001-v0.5-consumer-wireframes.md`, ADR-003 (ledger), ADR-004 (idempotency), ADR-008 (payment adapter), `v0.5-demo-plan.md §4` (Paystack sandbox in V0.5).

---

## 0. Why this flow is the hinge of the demo

Two reasons.

First: **this is where the mechanic becomes real for the user.** The skill question is not chrome. It is the moment the user experiences prize-competition-not-lottery in her thumb, not in a T&C footnote. If this moment feels like a game-show gimmick, the tone breaks. If it feels like a considered gate, the tone holds.

Second: **this is the money moment.** Paystack sandbox is a webview interlude — a period where the user leaves the Atlas surface and comes back. That handoff is the single most fragile UX moment in the app. If it fails silently, the user has entered a limbo they cannot navigate out of. Getting the *return* from Paystack right — success, failure, abandonment, timeout, duplicate-webhook — is more design work than getting the outbound journey right.

**Non-goals for V0.5:**
- Multiple ticket quantity in one purchase. V1. V0.5 is one entry per purchase (documented in `v0.5-demo-plan.md §3` — extends to "buy N in one go" in V1).
- Saved cards / one-tap payment. V1.
- Alternative payment rails (bank transfer, USSD). V1 per ADR-008.
- Wallet top-up model. V0.5 is direct-charge-per-entry only. Wallet flows are a V1 conversation.
- 3-D Secure explicit UI — Paystack's sandbox handles it; we route the webview.
- Refunds from this surface. Refunds are operator-initiated per plan §3.

---

## 1. Flow overview

```
                             (from wireframe 02 §3
                              — Enter button)
                                    │
                                    ▼
                        ┌──────────────────────┐
                        │  Screen 4.1          │
                        │  Skill question      │
                        │  intro + question    │
                        └──────────┬───────────┘
                                   │ correct answer
                                   ▼
                        ┌──────────────────────┐
                        │  Screen 4.2          │
                        │  Order review        │
                        │  (price, entry rules,│
                        │   idempotency safety │
                        │   net)               │
                        └──────────┬───────────┘
                                   │ Pay
                                   ▼
                        ┌──────────────────────┐
                        │  Screen 4.3          │
                        │  Paystack sandbox    │
                        │  webview (external)  │
                        └──────────┬───────────┘
                          success  │  fail/abandon
                          ┌────────┴────────┐
                          ▼                 ▼
                ┌──────────────────┐   ┌──────────────────┐
                │  Screen 4.4      │   │  Screen 4.5      │
                │  Ticket issued   │   │  Payment result  │
                │  (celebration    │   │  (failure /      │
                │   moment, brief) │   │   abandon states)│
                └────────┬─────────┘   └────────┬─────────┘
                         │                      │
                         ▼                      ▼
                (→ wireframe 05,        (return to 4.2 order
                 My tickets)              review with retry)
```

Five screens total in this flow. Screen 4.3 is Paystack sandbox — not our surface but our design work all the same, because the *return path* is ours.

---

## 2. Screen 4.1 — Skill question

### 2.1 Layout

```
┌─────────────────────────────────────────┐
│                                         │
│  ← Back                                 │  ← top bar, opaque surface.base
│                                         │      (photograph is behind us now)
│                                         │
│                                         │  space.800
│                                         │
│  ▪ 1 of 1                               │  ← type.label.micro uppercase gold
│                                         │      (position in sequence — reads as
│                                         │       a considered ritual, not a wall)
│                                         │  space.400
│                                         │
│  One question before you enter.         │  ← type.display.card (24pt Fraunces)
│                                         │
│  Atlas competitions are decided on the  │  ← type.body.default, secondary
│  same terms whether you pay or not —    │
│  the question confirms your entry.      │
│                                         │
│                                         │  space.1200
│                                         │
│  Which of these is the capital of       │  ← type.display.card (24pt Fraunces)
│  Nigeria?                               │      color.text.primary
│                                         │
│                                         │  space.800
│                                         │
│  ┌───────────────────────────────────┐ │  ← AnswerChip, unselected
│  │  A     Lagos                       │ │      radius.pill, hairline border,
│  │                                    │ │      surface.base, 56pt tall
│  └───────────────────────────────────┘ │
│                                         │  space.300
│  ┌───────────────────────────────────┐ │
│  │  B     Abuja                       │ │
│  │                                    │ │
│  └───────────────────────────────────┘ │
│                                         │  space.300
│  ┌───────────────────────────────────┐ │
│  │  C     Kano                        │ │
│  │                                    │ │
│  └───────────────────────────────────┘ │
│                                         │  space.300
│  ┌───────────────────────────────────┐ │
│  │  D     Ibadan                      │ │
│  │                                    │ │
│  └───────────────────────────────────┘ │
│                                         │
│                                         │  space.1200
│                                         │
│  (no CTA — selecting an answer          │
│   advances the flow immediately after   │
│   a 400ms confirm state — see §2.3)     │
│                                         │
└─────────────────────────────────────────┘
```

### 2.2 Components used

- `TopBar` — back variant, opaque `surface.base` (no more photograph backdrop).
- `SectionLabel` — gold eyebrow, here used as a position indicator ("1 of 1").
- `SectionHeadline` — 24pt Fraunces for both the intro line and the actual question. Two headline moments on the same screen is unusual — intentional here because the intro is the tone-carrying moment ("Atlas is a prize competition, not a lottery") and the question is the mechanic-carrying moment. Both earn display weight.
- `AnswerChip` — new component, `radius.pill` (this is one of only two places pill radius is used, per `tokens.md §4`). 56pt tall. Contains a letter label (A/B/C/D) and answer text.

### 2.3 States

**Default:** as drawn. All chips unselected. No CTA.

**Answer tapped (correct):**
1. Chip flashes to `color.state.success` background with `color.text.inverted` text for 400ms.
2. A small check icon fades in on the right of the chosen chip.
3. Screen auto-navigates to Screen 4.2 (order review).

**Answer tapped (incorrect):**
1. Chip flashes to `color.state.danger` background for 400ms, then returns to default.
2. All other chips shake gently (Flutter `TweenAnimationBuilder` — 4pt horizontal, 120ms).
3. Inline error appears above the chips: *"Not quite. Try another answer."* in `color.state.danger` at `type.body.small`.
4. After 3 wrong answers in a row, the error text updates: *"Take your time. There's no penalty for trying again."* — this softens the tone; we do not want a user feeling penalised at the *pre-payment* stage.

**Loading (validating with backend — should be near-instant since answer validation is client-visible-but-server-authoritative):** faint shimmer on the tapped chip until confirmation returns. Almost always < 100ms; if > 200ms, chip shows spinner in place of the check.

**Backend unavailable:** page-level banner *"We couldn't confirm the answer. Check your connection and try again."*

### 2.4 Copy

| Element | Copy |
|---|---|
| Position label | 1 of 1 |
| Intro headline | One question before you enter. |
| Intro subhead | Atlas competitions are decided on the same terms whether you pay or not — the question confirms your entry. |
| Skill question (seed example) | Which of these is the capital of Nigeria? |
| Answers (seed) | Lagos · Abuja · Kano · Ibadan |
| Error (1–2 wrong) | Not quite. Try another answer. |
| Error (3+ wrong) | Take your time. There's no penalty for trying again. |
| Connectivity error | We couldn't confirm the answer. Check your connection and try again. |

**Copy commentary:**

- The intro line *"Atlas competitions are decided on the same terms whether you pay or not — the question confirms your entry."* is the second appearance of the equal-terms phrasing (first is on the disclosure sheet, wireframe 03 §3.4). Repetition is deliberate: reinforcing the mechanic across surfaces makes the framing feel structural, not slogan-y. **Amended 2026-07-08 per REVIEW-001 §3.3** — the original draft used the *"prize competition, not a lottery"* legal classification claim; Adaeze required consistent substitution across both wireframes. The pattern is bounded to two surfaces per §3.3; a third appearance elsewhere reads as protesting too much.
- Answers deliberately include one *plausible-wrong* (Lagos — the ex-capital that many still mentally treat as capital) and two *obvious-wrong* (Kano, Ibadan). The question difficulty is calibrated: not so easy it feels rhetorical, not so hard it becomes a barrier. Adaeze/legal should confirm the difficulty level is defensible as a genuine skill test.
- No exclamation marks anywhere — including the "Not quite" error. *"Not quite"* is the tone.
- No congratulatory copy on correct answer. The auto-advance IS the congratulation. Adding *"Correct!"* or *"Well done!"* would tip into game-show — exactly what tone-doc.md §6 rejects.

### 2.5 Accessibility

- **Focus order:** Back → Skill question (announced with position label) → Answer A → B → C → D. First answer chip receives focus on mount.
- **Chip semantics:** `role="radio"` grouped inside `role="radiogroup"` labelled by the question. Screen-reader announces *"Radio button 1 of 4, Lagos, unselected. Which of these is the capital of Nigeria."*
- **Selection announcement:** on tap, correct or incorrect state is announced via `aria-live="assertive"` region above the chips. Correct: *"Correct answer. Continuing to order review."* Incorrect: *"Not quite. Try another answer."*
- **Colour-independence:** correct/incorrect never signalled by colour alone — always accompanied by the icon (check) or text.
- **Contrast:** state.success on state.success (chip fill) with text.inverted = 5.9:1 ✅. state.danger with text.inverted = 4.7:1 ✅.
- **Touch targets:** each chip 56pt tall, full-width. Between-chip gap 12pt reduces mis-taps.
- **Reduce motion:** the shake animation on incorrect is skipped; chip flash duration cut to 200ms.

### 2.6 Interaction

- **Answer tap:** fires validation request (idempotent with `entry_attempt_id` from the previous step). On correct → auto-advance to Screen 4.2.
- **Back:** returns to draw detail (Screen 2.2). The `entry_attempt_id` is not consumed — user can re-enter the flow without a new attempt being created.
- **Deep-link into this screen:** not supported. Requires an in-progress `entry_attempt_id` from the Enter button.

---

## 3. Screen 4.2 — Order review

### 3.1 Layout

```
┌─────────────────────────────────────────┐
│                                         │
│  ← Back                                 │
│                                         │
│                                         │  space.800
│                                         │
│  Your entry                             │  ← type.display.card (24pt Fraunces)
│                                         │
│                                         │  space.600
│                                         │
│  ┌───────────────────────────────────┐ │
│  │                                    │ │  ← OrderCard,
│  │  This week's draw                  │ │      radius.large, surface.elevated,
│  │  ₦2,000,000 in cash                │ │      elevation.0, 24pt padding
│  │  Closes 8pm Saturday, 12 July      │ │
│  │                                    │ │
│  │  ─────────────────────────────     │ │  ← hairline
│  │                                    │ │
│  │  One entry              ₦2,500     │ │  ← row: label + amount right-aligned
│  │                                    │ │      body.default
│  │  ─────────────────────────────     │ │
│  │                                    │ │
│  │  Total                  ₦2,500     │ │  ← row: body.emphasis both sides
│  │                                    │ │
│  └───────────────────────────────────┘ │
│                                         │
│                                         │  space.600
│                                         │
│  ┌───────────────────────────────────┐ │
│  │  ▪ You're about to be redirected   │ │  ← InfoNote — radius.large,
│  │                                    │ │      surface.base + hairline border,
│  │  Payment happens with Paystack.    │ │      body.default primary
│  │  You'll return here as soon as     │ │
│  │  it's done. Don't close the app.   │ │
│  └───────────────────────────────────┘ │
│                                         │
│                                         │  space.800
│                                         │
│  ┌───────────────────────────────────┐ │
│  │            Pay ₦2,500              │ │  ← primary button, 52pt,
│  └───────────────────────────────────┘ │      radius.medium
│                                         │
│                                         │  space.400
│                                         │
│  Cancel                                 │  ← inline link, centered
│                                         │      color.text.secondary
│                                         │
│                                         │  bottom safe area
└─────────────────────────────────────────┘
```

### 3.2 Components

- `TopBar` (back).
- `SectionHeadline`.
- `OrderCard` — new; composition of draw summary, line items, total. Reused in ticket detail (wireframe 05) for the "purchase" section.
- `InfoNote` — composition of a small gold square bullet + body copy. Used elsewhere to signal *"this is a considered piece of the flow, not a warning"*.
- `Button` (primary, dynamic label with amount).
- `InlineLink` (Cancel).

### 3.3 States

**Default:** as drawn.

**Pay tapped (loading):** button label becomes *"Opening payment…"* + inline spinner. Button non-interactive. Backend call fires to create the Paystack transaction and receive the sandbox URL.

**Paystack init failed:** button reverts. Banner: *"We couldn't open the payment. Try again in a moment."*

**Paystack init succeeded:** app hands off to Screen 4.3 (Paystack sandbox webview). This is where the user leaves our surface.

**Return from Paystack — success:** navigate to Screen 4.4.
**Return from Paystack — failure/abandon:** navigate to Screen 4.5.
**Return from Paystack — pending (rare, but Paystack can respond `pending`):** navigate to Screen 4.5 with pending state (see §5.3).

**Cancel tapped:** confirmation sheet *"Cancel this entry?"* / *"Nothing has been charged."* with a "Cancel entry" and "Keep going" button. If cancelled → return to draw detail.

**Idempotency safety net (visible to advanced users, invisible to normal flow):** if user hits Pay, backgrounds the app, and reopens ~30 seconds later, the state resumes. If the Paystack tx has already been created but not yet paid, we do NOT create a second one — the same tx is reopened. This is invisible to the user; it's stated here because the design must not accidentally trigger it (e.g., no auto-retry on button that would create a second tx).

### 3.4 Copy

| Element | Copy |
|---|---|
| Headline | Your entry |
| Card sub | This week's draw / ₦2,000,000 in cash / Closes 8pm Saturday, 12 July |
| Line item | One entry / ₦2,500 |
| Total | Total / ₦2,500 |
| Info note | You're about to be redirected. Payment happens with Paystack. You'll return here as soon as it's done. Don't close the app. |
| Primary CTA | Pay ₦2,500 |
| CTA loading | Opening payment… |
| Init failed banner | We couldn't open the payment. Try again in a moment. |
| Cancel link | Cancel |
| Cancel confirm title | Cancel this entry? |
| Cancel confirm body | Nothing has been charged. Your answer to the skill question is remembered if you come back. |
| Cancel confirm confirm | Cancel entry |
| Cancel confirm dismiss | Keep going |

**Copy commentary:**

- Amount on the button (*"Pay ₦2,500"*, not just *"Pay"*) is a small trust cue — the user sees the exact amount she's about to commit to on the button, no surprise on the Paystack screen.
- The InfoNote uses the same gold-bullet treatment as the free-entry disclosure (wireframe 03). Same visual language means "this is a considered part of the product". The phrase *"Don't close the app"* is a small trust risk (feels controlling) but the alternative (silent redirect with no warning) is worse. Kept as-is; open to founder push-back.
- *"Your answer to the skill question is remembered if you come back."* on cancel is a small kindness — signals we don't force re-answer if the user changes her mind then returns.

### 3.5 Accessibility

- **Focus order:** Back → Order card (composite readable summary) → Info note (paragraph, no focus) → Pay button → Cancel link.
- **Card readable label:** *"Your entry. This week's draw. Two million naira in cash. Closes 8pm Saturday, 12 July. One entry, two thousand five hundred naira. Total, two thousand five hundred naira."*
- **Pay button announces amount:** *"Pay two thousand five hundred naira."*
- **Cancel confirmation sheet:** modal semantics, focus trapped, escape/back dismisses.
- **Contrast:** all pairings tokened.

### 3.6 Interaction

- **Pay tap:** fires backend call `POST /entries` with `Idempotency-Key: {entry_attempt_id}` per ADR-004. Backend creates a Paystack tx, returns hosted URL. App opens URL in `webview_flutter` with a JS bridge for return signalling.
- **Return from Paystack:** app receives Paystack's redirect URL, parses status, navigates accordingly. See §5 for the return-handling contract.
- **Cancel confirmed:** `entry_attempt_id` is abandoned server-side (soft-cancel); user returns to draw detail.
- **App backgrounded during Paystack:** on resume, if user is still on Paystack URL, keep webview alive. If user has completed Paystack but app was killed, on next open, the "resume in-progress purchase" path is triggered — see §5.4.

---

## 4. Screen 4.3 — Paystack sandbox webview

### 4.1 Design ownership

Not our UI to design — this is Paystack's hosted checkout page. What IS our design work here:

- **Header/chrome around the webview:** a slim top bar with *"Paying with Paystack"* label + a Cancel link. NO back arrow (back-out of an in-progress payment is a source of duplicate-tx bugs — force user through the explicit Cancel).
- **Loading treatment:** while Paystack's page loads, we show our own *"Opening Paystack…"* skeleton screen (Atlas branded) rather than a blank white flash. Duration typical <1.5s.
- **Error handling on webview:** if Paystack page fails to load (network, DNS), we show our own error page with retry:
  > We couldn't reach Paystack. Check your connection and try again.

  Retry re-opens the same URL (idempotent). Cancel returns to Screen 4.2.
- **Interception of the return URL:** the JS bridge listens for Paystack's callback URL. On match, close the webview and navigate to 4.4 or 4.5.

### 4.2 States

**Loading:** Atlas skeleton screen ~ 1s max.
**Loaded:** Paystack's UI, full-screen inside Atlas app.
**Error loading:** Atlas error page + retry.
**Success return:** Atlas dismisses webview → 4.4.
**Failure return:** Atlas dismisses webview → 4.5.

### 4.3 Copy (Atlas-side only)

| Element | Copy |
|---|---|
| Loading label | Opening Paystack… |
| Load error | We couldn't reach Paystack. Check your connection and try again. |
| Cancel link | Cancel |
| Cancel confirmation | Cancel this payment? Nothing will be charged. |
| Header label | Paying with Paystack |

### 4.4 Accessibility

- Header label is announced on mount.
- Cancel is announced with confirmation (destructive-safe).
- The Paystack page itself carries its own AT semantics; we do not intercept.

---

## 5. Screen 4.4 — Ticket issued (celebration, brief)

### 5.1 Layout

```
┌─────────────────────────────────────────┐
│                                         │
│                                         │  space.1600
│                                         │
│                                         │
│              ✓                          │  ← 64pt gold check-in-circle
│                                         │      color.brand.accent
│                                         │
│         You're in.                      │  ← display.section, centered
│                                         │
│    Ticket 04829                         │  ← display.card, centered
│                                         │      body.mono for the number
│                                         │
│                                         │  space.800
│                                         │
│         Draw closes 8pm Saturday.       │  ← body.default, centered secondary
│              We'll be in touch.         │
│                                         │
│                                         │  space.1600
│                                         │
│  ┌───────────────────────────────────┐ │
│  │        See your tickets            │ │  ← primary button, full width but
│  └───────────────────────────────────┘ │      with margin (not full-bleed)
│                                         │      space.400
│  Back to Atlas                          │  ← inline link, centered secondary
│                                         │
└─────────────────────────────────────────┘
```

### 5.2 Components

- `SplashCheck` — reused from wireframe 01 §5 (welcome screen). Same gold check + label formula. The reuse is deliberate — this establishes a "successful commitment complete" moment across the product.
- `Button` (primary).
- `InlineLink`.

### 5.3 States

**Default (post-payment-success):** as drawn.

**Loading (ticket issuance in progress, rare — Paystack has confirmed but our idempotent ticket-issue call is in flight):** headline is *"Confirming your entry…"*, spinner replaces the check icon, no CTAs visible. Typically <500ms; if > 3s, show a soft explanation: *"Almost there — Paystack's confirmed the payment, we're just recording your ticket."*

**Failure (ticket issuance failed after payment succeeded — very rare, ADR-004 idempotency + outbox pattern per ADR-002 should make this recoverable):** this is a critical failure mode. Route to Screen 4.5 with a special *"payment_succeeded_ticket_pending"* state that surfaces support contact.

### 5.4 Copy

| Element | Copy |
|---|---|
| Headline | You're in. |
| Ticket line | Ticket 04829 |
| Subtext | Draw closes 8pm Saturday. We'll be in touch. |
| Primary CTA | See your tickets |
| Secondary link | Back to Atlas |
| Loading headline | Confirming your entry… |
| Loading detail (after 3s) | Almost there — Paystack's confirmed the payment, we're just recording your ticket. |

**Copy commentary:**

- *"You're in."* is intentionally the same phrase as the welcome-on-first-registration screen (wireframe 01 §5.4). Repetition creates ritual — the two "You're in" moments (first sign-up, first ticket) become anchors for the user's sense of the product.
- *"We'll be in touch."* is a promise that has to be honoured. Notifications-on-reveal is flagship step 6 (wireframe 06).
- No exclamation marks. No confetti. No *"Congratulations!"*.

### 5.5 Accessibility

- Announcement on mount: *"You're in. Ticket 04829. Draw closes 8pm Saturday. We'll be in touch."* via `aria-live="assertive"`.
- Ticket number read digit-by-digit (*"zero four eight two nine"*) not as a large number.
- Reduce motion: check appears solid; no scale-in animation.

### 5.6 Interaction

- **See your tickets:** navigates to My tickets (wireframe 05).
- **Back to Atlas:** navigates to Home (screen 2.1).
- **Auto-navigate?** No. Unlike the welcome screen (wireframe 01), this screen holds — the user should be the one who taps forward, because *the ticket number is worth reading*.

---

## 6. Screen 4.5 — Payment result (failure / abandon / pending)

### 6.1 Layout (failure variant)

```
┌─────────────────────────────────────────┐
│                                         │
│  ← Back                                 │
│                                         │
│                                         │  space.1600
│                                         │
│                                         │
│              ⚠                          │  ← 64pt terracotta warning glyph
│                                         │      color.state.danger
│                                         │      (glyph, not filled shape)
│                                         │
│                                         │
│         Payment didn't go through.      │  ← display.card, centered
│                                         │
│                                         │  space.400
│                                         │
│    Nothing was charged. Try again,      │  ← body.default, centered secondary
│    or use a different card.             │
│                                         │
│                                         │  space.1600
│                                         │
│  ┌───────────────────────────────────┐ │
│  │            Try again               │ │  ← primary button
│  └───────────────────────────────────┘ │
│                                         │  space.400
│  Cancel this entry                      │  ← inline link, centered danger
│                                         │
└─────────────────────────────────────────┘
```

### 6.2 Variants (copy + glyph change)

| Variant | Glyph | Headline | Body |
|---|---|---|---|
| Failure (declined, network, generic Paystack error) | ⚠ terracotta | Payment didn't go through. | Nothing was charged. Try again, or use a different card. |
| Abandon (user closed Paystack window / hit Cancel there) | ⌀ text.secondary | You backed out of payment. | Nothing was charged. Ready to try again? |
| Pending (Paystack returned `pending` — rare, e.g. bank auth still in flight) | ⋯ attention amber | Payment is still processing. | We're waiting for your bank. This can take up to 15 minutes. We'll notify you either way. |
| **Critical: payment succeeded, ticket not yet issued** | ⚠ terracotta | Payment went through — we're finalising your ticket. | This shouldn't take more than a minute. If it does, contact us and quote reference **RE-04829**. |

The critical variant has a **hard support contact** — WhatsApp / email link (V0.5: mailto: only; WhatsApp is stubbed per plan). This is the one variant that a user is likely to be in real distress on, so it earns explicit support access.

### 6.3 Components

- `TopBar` (back).
- `StatusIcon` — reusable glyph in a state colour.
- `SectionHeadline` (display.card size — smaller than the "You're in" moment, deliberately less loud).
- `Button` (primary).
- `InlineLink` — Cancel this entry (color.state.danger).
- `SupportContact` — new component; used only on the critical variant (§6.2 last row).

### 6.4 Copy (per §6.2)

### 6.5 Accessibility

- Announcement on mount: full headline + body via `aria-live="assertive"`.
- Glyph has `aria-hidden` since headline conveys the state.
- Critical-variant reference number read digit-by-digit.

### 6.6 Interaction

- **Try again:** returns to Screen 4.2 (order review). The `entry_attempt_id` is retained; the *same* Paystack tx is retried (per idempotency).
- **Cancel this entry:** confirmation sheet (same pattern as §3.3), then return to draw detail.
- **Pending variant:** *"Try again"* is replaced by *"Back to Atlas"* — retrying a pending tx creates duplicate charges (would violate ADR-004). User is nudged to wait.

---

## 7. What happens outside these screens

Recording here because the design of these screens depends on backend behaviour behaving:

- **Idempotency (ADR-004):** every `POST /entries` carries `Idempotency-Key: entry_attempt_id`. Server-side, retries return the original result. The design assumes this — every "Try again" button relies on it.
- **Ledger (ADR-003):** payment success creates journal entries. Not visible on any screen in this flow. Consumer surface is deliberately unaware of double-entry mechanics.
- **Audit log (ADR-005):** every state transition (entry attempted, payment initiated, payment succeeded, ticket issued) writes to the hash-chained audit log. Not visible here; visible on the proof page (wireframe 12).
- **Outbox (ADR-002):** ticket-issued event triggers notification to the user via outbox. In V0.5, notification is Mailhog email + in-app toast.
- **Payment adapter (ADR-008):** V0.5 uses `PaystackSandbox`; V1 swaps in `PaystackLive` behind the same interface. Design copy makes no assumption about which is in use, except the *"Payment happens with Paystack"* line — same phrasing works for V0.5 and V1.

---

## 8. Open questions for founder + agents

### For founder:

1. **Auto-advance on correct answer (Screen 4.1)** — no explicit Continue button. If you prefer a two-tap experience for reversibility, we add a Continue. Recommend keep auto-advance: two taps feels bureaucratic; one tap + 400ms confirm animation is enough.
2. **"Don't close the app" copy on the order-review info note (§3.4).** Slightly controlling. Alternative wording: *"Keep the app open — you'll come straight back."* Recommend the alternative.
3. **Reuse of "You're in." across registration success and ticket issued.** Deliberate as a ritual anchor. If it feels *too* repetitive, we differentiate — but I'd hold.
4. **Ticket number typography.** Currently `body.mono` (JetBrains Mono) — same font family as the commitment hash. This ties tickets and proofs into the same visual language. Alternative: Fraunces (feels ceremonial). Recommend mono for consistency with the trust story.
5. **No wallet, no saved cards for V0.5.** Every purchase is a fresh Paystack round-trip. Confirms scope? (This IS in `v0.5-demo-plan.md §3`, so a re-confirm rather than a decision.)

### For ⚖️ Adaeze — RESOLVED 2026-07-08 by REVIEW-001

6. **Skill question difficulty** — resolved §3.1: current seed question *approved for V0.5 demo only*; **rejected for real-user launch**. Adaeze owns the Phase 3 question-pool architecture at `docs/compliance/skill-questions.md`. Also flagged in REVIEW-001 §6.2: V0.5 has no rate-limit or lockout after N wrong answers so the "filter" is theatrical; a 3-strike + cooldown is a real-launch Ticket-module invariant. Tracked as R-SKILL-01.
7. **Rotation from seed pool** — resolved §3.2: pool stays private, per-user rotation ≥30 days, global rotation cap, difficulty variance managed. Ticket-module code-enforced invariant, not an operator knob. Amelia to build.
8. **Phrasing repetition** — resolved §3.3: approved, bounded to two surfaces, both amended above.

### For 💻 Amelia:

9. **Paystack sandbox redirect handling** — the JS-bridge intercept of the callback URL is the cleanest cross-platform pattern for `webview_flutter`. Confirm this approach works, or propose alternative (native SDK, deep-link callback).
10. **The "payment_succeeded_ticket_pending" edge case (§6.2 critical variant)** — how long is the outbox retry window before we surface support contact? Suggested UI threshold: 60 seconds. What's the operational reality?
11. **Backgrounding during Paystack webview** — Flutter `webview_flutter` behaviour on iOS vs Android when app is backgrounded needs testing. If we lose the webview on background/resume, design must switch to a "resume payment" screen on cold-return.

---

## 9. Cross-references

- Host wireframe (Enter tapped from here): `02-browse-active-draw.md §3.6`.
- Destination: `05-my-tickets.md` — where "See your tickets" goes.
- Free-entry equivalent (must use the SAME skill question copy): `03-free-entry-disclosure.md` + the Day-12 full free-entry-route page.
- Tokens: `tokens.md`.
- Tone: `tone-doc.md` §5 (copy voice), §6 (what Atlas is NOT).
- ADRs: ADR-002 outbox, ADR-003 ledger, ADR-004 idempotency, ADR-008 payment adapter.
- Plan: `v0.5-demo-plan.md §2` (step 4), §3 (V0.5 exclusions — no wallet, no saved cards), §4 (V0.5 architecture — Paystack sandbox).

---

🎨 *End of wireframe 04. Ticket card (wireframe 05) next — this is the Anchor 3 Range Rover moment, and it gets its own extended treatment.*

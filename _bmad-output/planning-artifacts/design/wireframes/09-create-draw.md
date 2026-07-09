# Wireframe 09 — Create Draw

**Drafted:** 2026-07-08 (Day 8 per `tone-doc.md §8`)
**Drafted by:** 🎨 Sally (BMad UX Designer)
**Status:** Draft — pending founder review AND ⚖️ Adaeze compliance review (skill-question assignment surface, publication of commit hash, no-going-back UX around the commit action) at end of Week 2.
**Covers:** Flagship flow step 9 from `v0.5-demo-plan.md §2` — *"Create draw — form: prize description, ticket price, entries cap, close time, draw time, skill question set. Publish commit hash on save."*
**Surface:** Next.js admin — inherits the admin shell from wireframe 08 §1.
**Pairs with:** `08-admin-login.md` (shell), `10-transcribe-free-entry.md` (Day 9), `11-close-and-reveal-draw.md` (Day 9 — the other end of the commit-reveal lifecycle), `tokens.md`, `tone-doc.md`, ADR-006 (commit-reveal protocol — the ADR whose consumer-visible artefacts this screen produces).

---

## 0. Why this screen is more consequential than it looks

*"Create draw"* sounds like a form. It is, mechanically. But the moment the operator taps *Publish* on this form, the following happens **irreversibly**:

- A `server_seed` (32 random bytes) is generated and stored encrypted (ADR-006 §Protocol stage 1).
- The `commitment = SHA-256(server_seed || draw_id)` is computed and **published to the consumer draw page, the audit log, and the `/api/v1/draws/{id}/proof` endpoint.**
- The draw's parameters (prize, price, close time, reveal time, skill question set) become part of the sealed commitment — changing them after commit is either impossible (immutable fields) or produces a visible audit-log amendment event that undermines the trust story.

The consumer sees a draw appear. The audit log gains a `draw.committed` entry. The world can now verify that Atlas committed to a specific set of draw parameters at a specific time and cannot secretly change them.

**Design implications:**

1. The commit step must not be triggered accidentally. A stray keypress or a mis-tapped button must not commit a real draw. This means the *Publish* button is a two-stage action, not a one-tap action (§3.5 confirmation step).
2. The operator must see, before committing, exactly what will be published. This means a *review* step precedes *publish*, showing the exact card the consumer will see (§3.4 review step).
3. The commit is auditable to Atlas the operator as well as to the world. On successful commit, the operator sees the commitment hash, the timestamp, and a receipt — not just a green tick (§3.6 confirmation state).
4. If a mistake is made post-commit (wrong prize amount, wrong close time), the operator's only options are (a) cancel the draw with a visible audit-log cancellation event or (b) run the draw and eat the mistake. There is no *"edit after commit"* path. This is a feature, not a bug — and the UX must make it clear before commit so mistakes are caught in review, not after.

Everything below serves those four implications.

**Non-goals for V0.5:**
- Prize image upload flow with cropper, filters, alt-text guidance. V0.5 accepts an image URL (from a pre-approved S3 bucket) or a placeholder. V1 gets a real uploader.
- Draw templates ("create like last week's draw"). V1.
- Recurring draws ("every Saturday at 8pm"). V1.
- Prize categories other than cash. V0.5 seed is cash prize only per plan §3.
- Multi-currency. Nigerian Naira only.
- Draw preview across the entire consumer flow (browse → detail → skill question → payment). The review step (§3.4) shows the consumer draw card only; the founder can walk the full flow post-publish before showing to investors.

---

## 1. Flow overview

```
        (sidebar → OPERATE → Draws → "New draw" button)
                            │
                            ▼
                ┌──────────────────────┐
                │  Screen 9.1          │
                │  Prize + timing      │
                │  (form step 1)       │
                └──────────┬───────────┘
                           │ Next
                           ▼
                ┌──────────────────────┐
                │  Screen 9.2          │
                │  Skill questions     │
                │  (form step 2)       │
                └──────────┬───────────┘
                           │ Next
                           ▼
                ┌──────────────────────┐
                │  Screen 9.3          │
                │  Review              │
                │  (what will be       │
                │   published)         │
                └──────────┬───────────┘
                           │ Publish
                           ▼
                ┌──────────────────────┐
                │  Modal 9.4           │
                │  "Publish this draw?"│
                │  (confirmation)      │
                └──────────┬───────────┘
                           │ Confirmed
                           ▼
                ┌──────────────────────┐
                │  Screen 9.5          │
                │  Published           │
                │  (commit receipt)    │
                └──────────────────────┘
```

Five screens: three form steps + one modal + one confirmation. **The commit action is on the modal, not on any of the previous screens** — this is the two-stage gate.

---

## 2. Entry point — "Draws" list (short)

Before Screen 9.1, the operator lands on the Draws index at `/admin/draws`. Not designed in full here — this is one of the operator surfaces that lives inside the shell and displays a table of draws with status. Layout sketch:

```
< inside admin shell >

  Draws                                        [ + New draw ]  ← primary button, top-right

  ─────────────────────────────────────────────────────────
  Draw                    Status      Entries    Close time
  ─────────────────────────────────────────────────────────
  ₦2,000,000 cash draw    ● Active    247        Sat 8pm
  ─────────────────────────────────────────────────────────

  (V0.5 will typically show one row here — the seeded active draw.)
```

Tapping `+ New draw` opens Screen 9.1.

---

## 3. Screen 9.1 — Prize + timing (form step 1)

### 3.1 Layout (inside admin shell)

```
< inside admin shell — 24pt padding on content region >

  ← Back to draws

  space.400

  ●●○   Step 1 of 3 · Prize and timing         ← ProgressIndicator (3 dots)
                                                  reused from wf-07 §3
                                                  gold uppercase label
  space.800

  Prize and timing                              ← type.display.card (24pt Fraunces)

  What are you drawing, when does it close,     ← body.default, secondary
  and when is the winner revealed?

  space.800

  ┌──────────────────────────────────────────────────────────┐
  │  ▪ Prize                                                 │  ← Section grouping —
  │                                                          │      radius.large surface.elevated
  │  ┌────────────────────────────────────────────────────┐ │      hairline border
  │  │ Prize title                                        │ │      elevation.0, 24pt padding
  │  ├────────────────────────────────────────────────────┤ │
  │  │ ₦2,000,000 in cash                                │ │  ← text input, 48pt
  │  └────────────────────────────────────────────────────┘ │      required
  │  Appears as the headline on the draw card and detail    │  ← body.small, secondary
  │  page.                                                   │      (helper text)
  │                                                          │
  │  ┌────────────────────────────────────────────────────┐ │
  │  │ Prize category                                     │ │
  │  ├────────────────────────────────────────────────────┤ │
  │  │ [ Cash                                        ▾ ]  │ │  ← dropdown; V0.5 = Cash only
  │  └────────────────────────────────────────────────────┘ │
  │                                                          │
  │  ┌────────────────────────────────────────────────────┐ │
  │  │ Cash amount (₦)                                    │ │
  │  ├────────────────────────────────────────────────────┤ │
  │  │ 2000000                                            │ │  ← numeric; renders below
  │  └────────────────────────────────────────────────────┘ │      as ₦2,000,000
  │  Renders as ₦2,000,000 on the consumer surface.         │
  │                                                          │
  │  ┌────────────────────────────────────────────────────┐ │
  │  │ Prize image URL                                    │ │
  │  ├────────────────────────────────────────────────────┤ │
  │  │ s3://atlas-prize-images/cash-2m-2026-07.jpg       │ │
  │  └────────────────────────────────────────────────────┘ │
  │  Must be a URL under our approved prize-image bucket.   │
  │  V1 replaces this with a real uploader.                  │
  │                                                          │
  │  ┌────────────────────────────────────────────────────┐ │
  │  │ Prize image alt text                               │ │
  │  ├────────────────────────────────────────────────────┤ │
  │  │ A stack of new ₦1,000 notes on a warm wooden      │ │
  │  │ surface.                                           │ │
  │  └────────────────────────────────────────────────────┘ │
  │  Read by screen readers on the consumer draw page.       │
  │  Required — accessibility.                                │
  └──────────────────────────────────────────────────────────┘

  space.600

  ┌──────────────────────────────────────────────────────────┐
  │  ▪ Entry mechanics                                       │
  │                                                          │
  │  ┌────────────────────────────────────────────────────┐ │
  │  │ Entry price (₦)                                    │ │
  │  ├────────────────────────────────────────────────────┤ │
  │  │ 2500                                               │ │  ← required, numeric
  │  └────────────────────────────────────────────────────┘ │
  │  Renders as ₦2,500 per entry.                            │
  │                                                          │
  │  ┌────────────────────────────────────────────────────┐ │
  │  │ Maximum paid entries (optional cap)                │ │
  │  ├────────────────────────────────────────────────────┤ │
  │  │ 10000                                              │ │  ← optional
  │  └────────────────────────────────────────────────────┘ │
  │  Leave empty for uncapped. Cap applies to paid entries   │
  │  only; the free route is not counted against the cap.    │
  │                                                          │
  │  ┌────────────────────────────────────────────────────┐ │
  │  │ Reserves                                           │ │
  │  ├────────────────────────────────────────────────────┤ │
  │  │ 5                                                  │ │  ← required, numeric,
  │  └────────────────────────────────────────────────────┘ │      default 5 per ADR-006
  │  Number of reserve winners drawn in order if the         │
  │  primary winner fails KYC or declines. Default 5.         │
  └──────────────────────────────────────────────────────────┘

  space.600

  ┌──────────────────────────────────────────────────────────┐
  │  ▪ Timing                                                │
  │                                                          │
  │  ┌────────────────────────────────────────────────────┐ │
  │  │ Sales open time                                    │ │
  │  ├────────────────────────────────────────────────────┤ │
  │  │ 08 Jul 2026, 14:00 (WAT)                          │ │  ← datetime picker
  │  └────────────────────────────────────────────────────┘ │
  │  When the draw appears on the consumer surface and       │
  │  entries begin. Timezone: West Africa Time (WAT, UTC+1). │
  │                                                          │
  │  ┌────────────────────────────────────────────────────┐ │
  │  │ Sales close time                                   │ │
  │  ├────────────────────────────────────────────────────┤ │
  │  │ 12 Jul 2026, 20:00 (WAT)                          │ │
  │  └────────────────────────────────────────────────────┘ │
  │  When sales stop. Free-route entries can be transcribed  │
  │  up to this time.                                         │
  │                                                          │
  │  ┌────────────────────────────────────────────────────┐ │
  │  │ Reveal time                                        │ │
  │  ├────────────────────────────────────────────────────┤ │
  │  │ 13 Jul 2026, 21:00 (WAT)                          │ │
  │  └────────────────────────────────────────────────────┘ │
  │  Must be ≥ 1 hour after close (ADR-006 requires this     │
  │  gap for public entropy to become available). When the   │
  │  winner is selected and announced.                        │
  └──────────────────────────────────────────────────────────┘

  space.1200

  [ Cancel ]                                     [ Next → ]

  (Cancel = inline link on the left; Next = primary button on the right)
```

### 3.2 Components used

- `AdminPageHeader` — back-link + step-progress-label + display headline + context sentence. Used on every multi-step admin form.
- `ProgressIndicator` — 3-dot variant, reused from wireframe 07 §3.1 but with a different dot count.
- `FormGroupCard` — a bordered card that visually clusters related fields under a gold section eyebrow. New but simple.
- `TextInput` / `NumberInput` / `Dropdown` / `DateTimeInput` — form primitives. Each has:
  - Label above (label.micro, uppercase).
  - Required `▪` bullet where relevant (per tokens spec).
  - Helper text below in body.small secondary.
  - Error state (danger colour + inline error text).
- `Button` (primary + secondary variants; `Next` uses primary).
- `InlineLink` (Cancel).

### 3.3 Validation

- **Prize title:** required, ≤ 80 chars.
- **Prize category:** V0.5 forced to "Cash".
- **Cash amount:** required, numeric, > 0, ≤ 1,000,000,000. Formatted with thousands separators on blur (`2000000` → `2,000,000`). The stored value is a Kobo-integer per ADR-003 (money-integer discipline, no floats) — the form input accepts Naira and multiplies by 100 on save. Helper text shows the Naira rendering for clarity.
- **Prize image URL:** required, must start with `s3://atlas-prize-images/` (V0.5 whitelist). V1 replaces with an uploader.
- **Prize image alt text:** required (accessibility), 10–200 chars.
- **Entry price:** required, > 0, must be a "clean" number (multiple of 100 preferred; helper text nudges but doesn't reject).
- **Max entries cap:** optional, if present must be > 0 and > entry-price × 1 (i.e. more than one entry allowed).
- **Reserves:** required, 1–20, default 5.
- **Sales open time:** required, must be ≥ 5 minutes in the future (prevents accidentally-past times).
- **Sales close time:** required, must be > sales open + at least 1 hour.
- **Reveal time:** required, must be ≥ 1 hour after close (ADR-006 constraint; the app enforces because if you set reveal < 1h after close, public entropy for that timestamp isn't available yet and the reveal fails).

### 3.4 States

**Default:** all required fields empty; Next disabled until all required fields have values that pass validation. Cancel available.

**Editing:** real-time validation on blur per field.

**Field errors:** below the field in `color.state.danger`, `body.small`.

**Cross-field errors** (e.g. close time before open time): appear as a page-level banner under the ProgressIndicator with a specific error line and jump-to-field link.

**Next tapped (loading):** button label *"Saving draft…"* + spinner. Form state saved server-side to a `draft_draws` row so the operator can resume from step 2 if they close the tab. This is important — losing the timing detail after 5 minutes of typing is bad UX.

**Cancel tapped:** confirmation modal *"Discard this draft? Nothing has been published."* → confirm returns to `/admin/draws`.

### 3.5 Copy

| Element | Copy |
|---|---|
| Back link | ← Back to draws |
| Step label | Step 1 of 3 · Prize and timing |
| Headline | Prize and timing |
| Context | What are you drawing, when does it close, and when is the winner revealed? |
| Group 1 eyebrow | Prize |
| Group 2 eyebrow | Entry mechanics |
| Group 3 eyebrow | Timing |
| Prize title label | Prize title |
| Prize title helper | Appears as the headline on the draw card and detail page. |
| Prize category label | Prize category |
| Cash amount label | Cash amount (₦) |
| Cash amount helper (dynamic) | Renders as ₦{formatted} on the consumer surface. |
| Prize image URL label | Prize image URL |
| Prize image URL helper | Must be a URL under our approved prize-image bucket. V1 replaces this with a real uploader. |
| Prize image alt label | Prize image alt text |
| Prize image alt helper | Read by screen readers on the consumer draw page. Required — accessibility. |
| Entry price label | Entry price (₦) |
| Entry price helper | Renders as ₦{formatted} per entry. |
| Max entries label | Maximum paid entries (optional cap) |
| Max entries helper | Leave empty for uncapped. Cap applies to paid entries only; the free route is not counted against the cap. |
| Reserves label | Reserves |
| Reserves helper | Number of reserve winners drawn in order if the primary winner fails KYC or declines. Default 5. |
| Sales open label | Sales open time |
| Sales open helper | When the draw appears on the consumer surface and entries begin. Timezone: West Africa Time (WAT, UTC+1). |
| Sales close label | Sales close time |
| Sales close helper | When sales stop. Free-route entries can be transcribed up to this time. |
| Reveal time label | Reveal time |
| Reveal time helper | Must be ≥ 1 hour after close (ADR-006 requires this gap for public entropy to become available). When the winner is selected and announced. |
| Cancel link | Cancel |
| Next CTA | Next → |
| Cancel confirm | Discard this draft? Nothing has been published. |

### 3.6 Accessibility

- **Focus order:** back-link → each form-group's fields top-to-bottom → Cancel → Next.
- **Field labels:** all `<label for>` associated, required indicator both visual (▪ gold) and semantic (`aria-required="true"`).
- **Helper text:** each field's helper linked via `aria-describedby`; announced on focus.
- **Cross-field error banner:** `aria-live="polite"`.
- **Datetime inputs:** use native pickers; announce the parsed value on blur (*"Selected: 12 July 2026, 8 pm West Africa Time"*).
- **Currency input:** on blur, formatted display doesn't change the underlying value; screen reader hears both (*"Two thousand five hundred naira"*).

### 3.7 Interaction

- **Field auto-save on blur.** Every valid field-change PATCHes the draft server-side. This makes the "save + close" implicit — closing the tab loses no data.
- **Datetime timezone.** All datetimes are captured in West Africa Time (WAT, UTC+1). The picker shows WAT; the server stores UTC. Consumer surface renders WAT.

---

## 4. Screen 9.2 — Skill questions (form step 2)

### 4.1 Layout

```
< inside admin shell >

  ← Back to draws

  space.400

  ●●●   Step 2 of 3 · Skill questions

  space.800

  Skill questions

  Every paid entry answers one skill question from the        ← body.default, secondary
  active pool. Free-route entries answer the same question
  on the entry slip. Rotation and difficulty are managed
  in the pool itself; here you just confirm which pool
  applies.

  space.800

  ┌──────────────────────────────────────────────────────────┐
  │  ▪ Skill question pool                                   │
  │                                                          │
  │  ┌────────────────────────────────────────────────────┐ │
  │  │ Active pool                                        │ │
  │  ├────────────────────────────────────────────────────┤ │
  │  │ [ V0.5 seed pool (4 questions)               ▾ ]  │ │  ← dropdown
  │  └────────────────────────────────────────────────────┘ │
  │  V0.5 has one seed pool. V1 gets multiple pools with     │
  │  category tagging.                                        │
  │                                                          │
  │  space.400                                                │
  │                                                          │
  │  Sample questions from this pool                         │  ← type.label.micro uppercase
  │                                                          │
  │  ┌────────────────────────────────────────────────────┐ │
  │  │ 1. Which of these is the capital of Nigeria?      │ │  ← preview cards, 3 shown
  │  │    Lagos · Abuja · Kano · Ibadan                  │ │      radius.medium surface.subtle
  │  │    (Correct: Abuja)                                │ │      hairline border
  │  │                                                    │ │      body.default primary
  │  ├────────────────────────────────────────────────────┤ │      body.small secondary for
  │  │ 2. Which colour appears on the Nigerian flag?     │ │      answers + correct
  │  │    Red · Yellow · Green · Blue                     │ │
  │  │    (Correct: Green)                                │ │
  │  ├────────────────────────────────────────────────────┤ │
  │  │ 3. What is 8 plus 5?                              │ │
  │  │    11 · 12 · 13 · 14                               │ │
  │  │    (Correct: 13)                                   │ │
  │  └────────────────────────────────────────────────────┘ │
  │                                                          │
  │  See all 4 questions →                                   │  ← inline link
  │                                                          │
  │  ┌───────────────────────────────────────────────────┐  │
  │  │  ⚠  V0.5 skill-question pool is DEMO ONLY.        │  │  ← WarningNote — new,
  │  │                                                    │  │      radius.large,
  │  │  Adaeze's REVIEW-001 §3.1 explicitly rejects      │  │      color.state.attention @ 12%
  │  │  this pool for real-user launch. Real-launch      │  │      background,
  │  │  question pool is a Phase 3 deliverable at        │  │      color.state.attention
  │  │  docs/compliance/skill-questions.md (owned by     │  │      solid 4pt left border
  │  │  Adaeze). Do not attach this pool to a draw       │  │      body.default primary
  │  │  intended for real users.                          │  │
  │  └───────────────────────────────────────────────────┘  │
  └──────────────────────────────────────────────────────────┘

  space.1200

  [ Cancel ]                        [ ← Back ]  [ Next → ]

  (Back = secondary button; Next = primary button)
```

### 4.2 Components used

- `AdminPageHeader`.
- `ProgressIndicator` — 3-dot now at 3/3 filled (progressing).
- `FormGroupCard`.
- `Dropdown` — pool selector.
- `QuestionPreviewCard` — new; stacked previews of first 3 questions in the pool with answers listed and the correct answer marked. Read-only.
- `InlineLink` — "See all N questions" (opens a modal listing the full pool for review).
- `WarningNote` — new; a full-width attention-coloured card noting that the V0.5 pool is demo-only. **This component makes Adaeze's REVIEW-001 §3.1 finding structurally visible in the admin so no future operator inadvertently attaches the demo pool to a real draw.**
- `Button` (primary Next, secondary Back).
- `InlineLink` (Cancel).

### 4.3 States

**Default:** V0.5 seed pool preselected (it's the only pool). First 3 questions preview visible. WarningNote visible.

**Pool switched (V1):** preview cards refresh; Next reactivates.

**"See all N questions" tapped:** modal opens showing all questions in the pool with answers, in a scrollable list. Close returns to this screen. No editing — the pool is managed elsewhere (V1 SETTINGS → Skill questions).

**Loading (Next tapped):** button label *"Saving draft…"*; state saved server-side.

### 4.4 Copy

| Element | Copy |
|---|---|
| Step label | Step 2 of 3 · Skill questions |
| Headline | Skill questions |
| Context | Every paid entry answers one skill question from the active pool. Free-route entries answer the same question on the entry slip. Rotation and difficulty are managed in the pool itself; here you just confirm which pool applies. |
| Group eyebrow | Skill question pool |
| Pool label | Active pool |
| Pool option (V0.5) | V0.5 seed pool (4 questions) |
| Pool helper | V0.5 has one seed pool. V1 gets multiple pools with category tagging. |
| Sample header | Sample questions from this pool |
| See-all link | See all {n} questions → |
| Warning heading | V0.5 skill-question pool is DEMO ONLY. |
| Warning body | Adaeze's REVIEW-001 §3.1 explicitly rejects this pool for real-user launch. Real-launch question pool is a Phase 3 deliverable at docs/compliance/skill-questions.md (owned by Adaeze). Do not attach this pool to a draw intended for real users. |
| Back CTA | ← Back |
| Next CTA | Next → |
| Cancel | Cancel |

### 4.5 Accessibility

- **Focus order:** back-link → pool dropdown → preview cards (individually — each has `role="article"`) → See-all link → Warning note (composite, announced as an alert) → Cancel → Back → Next.
- **Warning note:** `role="alert"` — this is the highest-attention text on the screen and should be announced first on mount. Not visually alarming (muted amber, not fire-engine red) but semantically an alert.
- **Preview cards:** each is `role="article"`, composite readable summary: *"Question 1. Which of these is the capital of Nigeria. Options: Lagos, Abuja, Kano, Ibadan. Correct answer: Abuja."*

### 4.6 Interaction

- **Preview cards are read-only.** No inline editing.
- **See-all link:** opens modal; modal closes back to this screen.
- **Pool dropdown (V1):** switches active pool for this draw; preview refreshes.

---

## 5. Screen 9.3 — Review (form step 3 — the "what will be published" step)

### 5.1 Layout

```
< inside admin shell >

  ← Back to draws

  space.400

  ●●●   Step 3 of 3 · Review

  space.800

  Review before publishing

  Once you publish, the draw's parameters are committed        ← body.default, secondary
  and cryptographically sealed. You cannot edit prize,
  timing, or skill questions after publishing — only cancel
  the whole draw (with a visible audit trail).

  Check everything below matches what you intended.

  space.800

  ┌──────────────────────────────────────────────────────────┐
  │  ▪ CONSUMER PREVIEW               [ Edit prize + timing ] │  ← ReviewSection with edit
  │                                                          │      link (returns to §3)
  │  ┌────────────────────────────────────────────────────┐ │
  │  │                                                    │ │  ← Rendered draw card,
  │  │         [ Prize photograph placeholder ]           │ │      identical to what the
  │  │                                                    │ │      consumer sees on wf-02 §2
  │  │                                                    │ │      Live-rendered from the
  │  │  ₦2,000,000                                        │ │      draft data.
  │  │  in cash                                           │ │
  │  │                                                    │ │
  │  │  ─────────────────────────                         │ │
  │  │  Closes 8pm Saturday                               │ │
  │  │  ₦2,500 per entry · 0 entries so far              │ │
  │  │                                                    │ │
  │  │  ┌──────────────────────────────┐                 │ │
  │  │  │        View draw             │                 │ │
  │  │  └──────────────────────────────┘                 │ │
  │  └────────────────────────────────────────────────────┘ │
  │                                                          │
  │  This is exactly what will appear on the consumer home   │  ← body.small secondary
  │  the moment sales open.                                   │
  └──────────────────────────────────────────────────────────┘

  space.400

  ┌──────────────────────────────────────────────────────────┐
  │  ▪ MECHANICS                        [ Edit prize + timing ]│
  │                                                          │
  │  Prize                    ₦2,000,000 in cash              │  ← definition-list row
  │  Entry price              ₦2,500                          │      label + value
  │  Max entries              10,000 (paid)                   │      body.default
  │  Reserves                 5                               │
  │  ────────────────────────────                             │
  │  Sales open               08 Jul 2026, 14:00 WAT          │
  │  Sales close              12 Jul 2026, 20:00 WAT          │
  │  Reveal                   13 Jul 2026, 21:00 WAT          │
  │  Sales window             4 days, 6 hours                 │
  │  Reveal after close       25 hours                        │
  │  ────────────────────────────                             │
  │  Skill question pool      V0.5 seed pool (4 questions)   │
  │                                                           │
  │  ⚠ Demo pool — see step 2 warning.                        │  ← body.small state.attention
  │                                                           │      (repeat of step 2 flag)
  └──────────────────────────────────────────────────────────┘

  space.400

  ┌──────────────────────────────────────────────────────────┐
  │  ▪ AFTER PUBLISH                                          │
  │                                                          │
  │  When you tap Publish:                                    │
  │                                                          │
  │  1. A random 32-byte server seed is generated             │  ← numbered list, body.default
  │     and encrypted at rest.                                │      body.small secondary sub-lines
  │                                                          │
  │  2. The seed's SHA-256 commitment hash is published      │
  │     to the consumer draw page, the audit log, and        │
  │     the public /proof endpoint.                          │
  │                                                          │
  │  3. The draw becomes visible to consumers at             │
  │     08 Jul 2026, 14:00 WAT (sales open time).            │
  │                                                          │
  │  4. Sales run until 12 Jul 2026, 20:00 WAT.              │
  │                                                          │
  │  5. Reveal fires at 13 Jul 2026, 21:00 WAT, using        │
  │     the server seed + Bitcoin block hash + drand round   │
  │     to select the winner.                                │
  │                                                          │
  │  The commitment cannot be reopened. Editing any of        │  ← body.default primary
  │  the fields above after publish is impossible without    │
  │  cancelling and recreating the draw — which produces      │
  │  a visible audit-log cancellation event.                  │
  └──────────────────────────────────────────────────────────┘

  space.1200

  [ Cancel ]                      [ ← Back ]  [  Publish draw  ]
                                                 ↑ primary button
                                                   color.state.attention subtle
                                                   background hint to signal
                                                   "this is a one-way action"
                                                   without shouting

  ⓘ Publish is guarded by a confirmation modal.                ← body.small secondary
                                                                   centred under button row
```

### 5.2 Components used

- `AdminPageHeader`.
- `ProgressIndicator`.
- `ReviewSection` — reused from wireframe 07 §7.2 (with the "Edit" link pattern; here the edit link returns to the corresponding step).
- `DrawCardPreview` — new; a live-rendered version of the consumer draw card using the draft data. **Renders using the same component the consumer surface uses**, not a static mock, so what the operator sees is truly what will appear.
- `DefinitionList` — new; a two-column label/value list. Used only on admin surfaces (consumer uses card-based layouts).
- `AfterPublishExplainer` — new; a bordered card with a numbered list of what will happen. Educational + guardrail.
- `Button` (primary + secondary).
- `InlineLink`.

### 5.3 States

**Default:** as drawn.

**Publish tapped:** opens modal 9.4.

**Back:** returns to Screen 9.2 with all state preserved.

**Cancel:** confirmation modal to discard the draft.

### 5.4 Copy

| Element | Copy |
|---|---|
| Step label | Step 3 of 3 · Review |
| Headline | Review before publishing |
| Context | Once you publish, the draw's parameters are committed and cryptographically sealed. You cannot edit prize, timing, or skill questions after publishing — only cancel the whole draw (with a visible audit trail). Check everything below matches what you intended. |
| Section 1 eyebrow | CONSUMER PREVIEW |
| Consumer-preview caption | This is exactly what will appear on the consumer home the moment sales open. |
| Section 2 eyebrow | MECHANICS |
| Section 3 eyebrow | AFTER PUBLISH |
| Step 1 | A random 32-byte server seed is generated and encrypted at rest. |
| Step 2 | The seed's SHA-256 commitment hash is published to the consumer draw page, the audit log, and the public /proof endpoint. |
| Step 3 | The draw becomes visible to consumers at {sales_open} (sales open time). |
| Step 4 | Sales run until {sales_close}. |
| Step 5 | Reveal fires at {reveal_time}, using the server seed + Bitcoin block hash + drand round to select the winner. |
| No-going-back sentence | The commitment cannot be reopened. Editing any of the fields above after publish is impossible without cancelling and recreating the draw — which produces a visible audit-log cancellation event. |
| Back CTA | ← Back |
| Publish CTA | Publish draw |
| Publish note | Publish is guarded by a confirmation modal. |
| Cancel | Cancel |

**Copy commentary:**

- **The AFTER PUBLISH section exists precisely because most admin forms don't have one.** Operators are used to *"save"* meaning *"you can edit later"*. In Atlas the commit action changes that contract — the review step must explicitly teach that. The numbered list gives the operator a specific mental model of what publish does, so the modal confirmation is a confirmation, not a surprise.
- The Publish button has a **subtle attention-coloured hint** in its background — not fire-engine red, not "danger", but a small visual cue that this action is different from an ordinary Save. The tokens permit this: `color.state.attention` at 12% opacity as a background hint on a primary button is a bounded exception. Confirm with founder if this treatment is right; alternative is to keep the button standard-primary and rely on the confirmation modal alone.

### 5.5 Accessibility

- **Focus order:** back-link → Consumer preview (composite) → Consumer-preview edit link → Mechanics (definition list, each row a `<dt><dd>`) → Mechanics edit link → After-publish list → Cancel → Back → Publish.
- **Preview card:** announced with a composite label including the sub-caption (*"Consumer preview. Prize card as consumers will see it. Two million naira in cash..."*).
- **After-publish list:** `role="list"` with each step a `listitem`; the closing paragraph is a normal `<p>`.
- **Publish button:** `aria-describedby="publish-note"` so screen-reader users hear *"Publish is guarded by a confirmation modal"* on focus.

### 5.6 Interaction

- **Publish:** opens modal 9.4. Button remains interactive (modal handles the actual commit).
- **Edit links:** navigate back to the corresponding form step. All entered state is preserved.

---

## 6. Modal 9.4 — Publish confirmation

### 6.1 Layout (modal, ~520pt wide)

```
< modal backdrop, elevation.2 >

  ┌────────────────────────────────────────┐
  │                                        │
  │  ▪ CONFIRM PUBLISH                     │  ← gold label.micro
  │                                        │
  │  Publish this draw?                    │  ← type.display.card
  │                                        │
  │  ─────────────────────────────         │
  │                                        │
  │  You're about to commit and publish:   │  ← body.default
  │                                        │
  │  ₦2,000,000 in cash                    │  ← body.emphasis primary
  │  Closes 12 Jul 2026, 20:00 WAT         │  ← body.default primary
  │  Reveals 13 Jul 2026, 21:00 WAT        │
  │                                        │
  │  ─────────────────────────────         │
  │                                        │
  │  Once published, the commitment is     │  ← body.default
  │  cryptographically sealed. Cancelling  │
  │  the draw after publish is possible    │
  │  but leaves an audit-log record.       │
  │                                        │
  │  Type PUBLISH to confirm:              │  ← body.default primary
  │  ┌────────────────────────────────┐   │
  │  │ PUBLISH                        │   │  ← text input, must literally
  │  └────────────────────────────────┘   │      contain "PUBLISH" to enable
  │                                        │      the confirm button
  │                                        │
  │  ─────────────────────────────         │
  │                                        │
  │  [ Cancel ]           [ Publish draw ] │  ← confirm button disabled until
  │                                        │      input equals PUBLISH
  │                                        │      space.400 above
  └────────────────────────────────────────┘
```

### 6.2 Components used

- `Modal` — centered, backdrop, focus-trapped, escape-dismissable.
- `TypedConfirmationInput` — new; the "type PUBLISH to confirm" pattern. Same discipline used elsewhere in high-stakes systems for irreversible actions (GitHub delete, Vercel project delete, etc.).
- `Button` (primary + secondary).

### 6.3 States

**Default:** confirm button disabled. Input empty.

**Input matches "PUBLISH":** confirm enables. Any other value keeps it disabled.

**Confirm tapped (loading):** button label *"Publishing…"* + spinner. Backend call fires:

1. `POST /admin/draws` with the full draft payload + `Idempotency-Key: {draft_id}`.
2. Server generates `server_seed`, computes `commitment`, encrypts seed, writes `draws` row, writes `draw.committed` audit-log event, returns the published draw + commitment.

**Commit succeeded:** modal closes; navigate to Screen 9.5 (published receipt).

**Commit failed (network / server error):** button reverts. Modal shows inline error: *"Publish didn't complete. Try again in a moment. No commitment was written."* — the last sentence is critical, tells the operator this is a safe retry.

**Cancel:** dismisses modal; returns to Screen 9.3 with all state preserved.

### 6.4 Copy

| Element | Copy |
|---|---|
| Eyebrow | CONFIRM PUBLISH |
| Headline | Publish this draw? |
| Body 1 | You're about to commit and publish: |
| Body 2 (summary) | {prize} / Closes {close}, {tz} / Reveals {reveal}, {tz} |
| Body 3 | Once published, the commitment is cryptographically sealed. Cancelling the draw after publish is possible but leaves an audit-log record. |
| Type-to-confirm prompt | Type PUBLISH to confirm: |
| Confirm CTA (default) | Publish draw |
| Confirm CTA (loading) | Publishing… |
| Cancel CTA | Cancel |
| Publish failed | Publish didn't complete. Try again in a moment. No commitment was written. |

### 6.5 Accessibility

- **Modal semantics:** `role="dialog"` `aria-modal="true"` `aria-labelledby="publish-modal-heading"`.
- **Focus trap:** confirmation input receives focus on open; Tab cycles between input, Cancel, and Confirm.
- **Type-to-confirm:** input is a standard `<input type="text">` with `autocomplete="off"`. The confirm button announces its enabled/disabled state on any input change via `aria-live="polite"` on a nearby helper span.
- **Escape:** dismisses; matches Cancel.
- **Reduce motion:** modal fades instead of slides.

### 6.6 Interaction

- **Type-to-confirm case sensitivity:** input must equal `PUBLISH` exactly (case-sensitive). Lowercase or mixed-case does not enable the button. This is deliberate friction; the small typing effort forces a moment of intention.
- **Backdrop click:** dismisses modal (equivalent to Cancel). No accidental commits from backdrop.
- **Idempotency:** the POST carries `Idempotency-Key = {draft_id}`. If the operator taps confirm twice (network stutter), the server returns the original commitment; no duplicate draws are created (ADR-004).

---

## 7. Screen 9.5 — Published (commit receipt)

### 7.1 Layout

```
< inside admin shell >

                                                    space.1200

                        ✓                            ← 48pt gold check
                                                        color.brand.accent

                Draw published.                       ← type.display.section, centered
                                                        color.text.primary

           ₦2,000,000 in cash draw is live.           ← body.default, secondary

                                                    space.1200

  ┌──────────────────────────────────────────────────────────┐
  │  ▪ COMMITMENT RECEIPT                                    │  ← gold eyebrow
  │                                                          │      radius.large,
  │                                                          │      surface.elevated
  │  Draw ID                DRAW-2026-07-08-A                │      elevation.0
  │                                                          │      24pt padding
  │  ─────────────────────────────                            │
  │                                                          │
  │  Commitment hash                                          │  ← label.micro secondary
  │  3f2c4b8e9a...8a91                    📋 Copy full hash  │  ← body.mono 16pt primary
  │                                                          │      truncated middle
  │  ─────────────────────────────                            │      copy full to clipboard
  │                                                          │
  │  Committed at           08 Jul 2026, 13:47:52 WAT         │
  │                                                          │
  │  Sales open at          08 Jul 2026, 14:00:00 WAT         │
  │                                                          │
  │  Sales close at         12 Jul 2026, 20:00:00 WAT         │
  │                                                          │
  │  Reveal at              13 Jul 2026, 21:00:00 WAT         │
  │                                                          │
  │  ─────────────────────────────                            │
  │                                                          │
  │  Published to:                                            │
  │  · Consumer draw page — atlas://draw/{draw_id}            │  ← body.small secondary
  │  · Audit log — event `draw.committed` #4829              │      URLs are inline links
  │  · Public /proof endpoint — atlas.ng/proof/{draw_id}     │      to those surfaces
  │                                                          │
  │  ─────────────────────────────                            │
  │                                                          │
  │  Save the commitment receipt as evidence of when Atlas   │  ← body.small secondary
  │  committed to this draw. This receipt is also available   │
  │  from the draw's audit-log entry.                         │
  │                                                          │
  │  [ Download receipt (JSON) ]                              │  ← secondary button
  └──────────────────────────────────────────────────────────┘

  space.800

  ┌────────────────────────┐  ┌──────────────────────────┐
  │   Go to draw page  →   │  │  View draw in admin  →   │
  └────────────────────────┘  └──────────────────────────┘
                              ← two side-by-side buttons,
                                 secondary variant

  space.400

  Create another draw                                        ← inline link, centered secondary
```

### 7.2 Components used

- `SplashCheck` — reused from consumer surface. Used here to close the loop — a commit is a considered moment; the check-in-circle motif ties admin trust ceremony to consumer trust ceremony.
- `CommitmentReceiptCard` — new; the load-bearing artefact of this screen. Composition: draw ID + hash row with copy affordance + timing definition list + published-to list + download-receipt button.
- `HashRow` — reused from consumer surface (wireframe 02 §3 draw-detail commitment-hash treatment). Same visual language for the same data.
- `Button` (secondary variants for the trailing actions).
- `InlineLink`.

### 7.3 States

**Only state.** No loading (data is present at render). No error (if we're here, publish succeeded).

### 7.4 Copy

| Element | Copy |
|---|---|
| Headline | Draw published. |
| Sub | {prize_title} draw is live. |
| Receipt eyebrow | COMMITMENT RECEIPT |
| Draw ID row | Draw ID / {draw_id} |
| Commitment hash label | Commitment hash |
| Commitment hash value | {truncated_hash} |
| Copy affordance | 📋 Copy full hash |
| Copy toast | Commitment hash copied. |
| Committed at label | Committed at |
| Sales open at label | Sales open at |
| Sales close at label | Sales close at |
| Reveal at label | Reveal at |
| Published-to header | Published to: |
| Published-to items | Consumer draw page — {url} / Audit log — event `draw.committed` #{event_id} / Public /proof endpoint — {url} |
| Receipt-save note | Save the commitment receipt as evidence of when Atlas committed to this draw. This receipt is also available from the draw's audit-log entry. |
| Download button | Download receipt (JSON) |
| Trailing action 1 | Go to draw page → |
| Trailing action 2 | View draw in admin → |
| Create-another link | Create another draw |

**Copy commentary:**

- **The receipt is not just a "you're done" screen.** It's evidence. The operator can download the JSON receipt (containing the hash, timestamps, and published URLs) as immediate proof that Atlas committed at a specific moment. This matters for a specific edge case: a regulator or auditor months later asking *"when did Atlas commit to this draw, and how do we know?"* — the answer is *"here's the receipt, here's the audit-log event ID, here's the public URL that has been publishing this hash since that moment."*
- The published-to list is a small trust move for the operator too — they see, on their own surface, all the places the commit has landed. It matches the surface-parity principle: what the operator sees the audit shows, and what the audit shows the operator sees.

### 7.5 Accessibility

- **Focus order:** page headline → receipt card (composite) → copy-hash affordance → download button → published-to links (individually) → trailing actions → Create-another link.
- **Receipt readable summary:** *"Commitment receipt. Draw I D DRAW dash 2026 dash 07 dash 08 dash A. Commitment hash 3 f 2 c 4 b 8 e 9 a truncated 8 a 9 1. Committed at 8 July 2026, 1 47 pm 52 seconds West Africa Time."* etc.
- **Download button:** `aria-label="Download commitment receipt as JSON"`.

### 7.6 Interaction

- **Copy hash:** copies full 64-char hex string. Toast confirms.
- **Download receipt (JSON):** browser download of a JSON file containing all receipt fields including the full hash and audit-log event ID. Filename: `atlas-commitment-{draw_id}-{committed_at}.json`.
- **Go to draw page:** opens the consumer draw page for this draw in a new tab (`atlas://draw/{id}` opens in the connected app in demo, or `atlas.ng/draw/{id}` in V1). Operator confirms visually that the commit landed as expected.
- **View draw in admin:** navigates to `/admin/draws/{id}` (draw detail — future wireframe).
- **Create another draw:** returns to Screen 9.1 with a fresh empty form.

---

## 8. Design invariants for the create-draw flow

Recording to protect against future drift:

1. **Publish is always a two-step action.** The Publish button on Screen 9.3 opens a modal; the actual commit is the type-to-confirm in the modal. No form of "quick publish" or "publish and skip review" should ever be introduced.
2. **The review step (Screen 9.3) shows the live consumer preview.** Not a mock, not a text description — the actual `DrawCard` component rendered from the draft data. If the preview drifts from the consumer surface's rendering, the review isn't a review.
3. **The commitment receipt (Screen 9.5) always shows the full published-to list.** The operator must always be able to see, in one place, where the commit landed.
4. **Post-commit edits are impossible on this surface.** The admin draw-detail page (future wireframe) may allow cancellation with an audit-log event, but this create-flow's "back" links are only reachable pre-commit.
5. **No "save as draft" naming ambiguity.** Every field's blur auto-saves the draft; Publish is the only save-as-committed action. Nothing else moves the draft closer to publish.
6. **The V0.5 skill-question warning stays visible until Adaeze ships the Phase 3 pool.** If the WarningNote is ever hidden or muted, the risk that a real-launch operator inadvertently attaches the demo pool becomes non-zero.

---

## 9. Open questions for founder + agents

### For founder:

1. **Type-to-confirm modal (§6).** Adds ~2 seconds of friction on publish. Alternative: single-confirm button with no typing. Recommend keep the typed pattern — the commit is irreversible; the small friction is worth it. If it feels excessive after the demo, we can drop to a single-tap confirm with a "hold to confirm" gesture (progress ring around the button).
2. **Publish button attention-tint (§5.4 commentary).** Currently the primary button has a subtle attention-colour background hint. Alternative: standard primary + rely on modal alone. Recommend keep tint — a small pre-commit visual cue reinforces the "this is different" signal.
3. **Timezone treatment (§3.5).** All datetimes are captured in WAT and always render with the `WAT` suffix. This is correct for a Nigeria-first product. When we expand to Ghana / Kenya, timezone selection becomes a per-draw setting.
4. **Sales-open time defaults.** Currently the operator sets sales-open manually. Alternative: default to "now" and let the operator override. Recommend the current explicit-set — a "goes live in 1 minute" trigger by accident is worse than a slightly slower form.
5. **Commitment receipt JSON download filename.** Currently `atlas-commitment-{draw_id}-{committed_at}.json` — makes the file searchable. Confirm.

### For ⚖️ Adaeze:

6. **The WarningNote on Screen 9.2 (V0.5 pool demo-only).** Structural visibility of the REVIEW-001 §3.1 finding. Wording review — is this accurate and appropriate for the admin surface?
7. **The AFTER PUBLISH explainer (§5.4).** Does the numbered list accurately describe what happens on commit, using operator-appropriate language? Any missing steps or misrepresentations?
8. **The commitment receipt (§7).** Adaeze — does this satisfy your audit-integrity concerns? Is anything missing that a compliance review or regulator would expect to see?
9. **The type-to-confirm word "PUBLISH".** Deliberate — matches consumer-side self-exclusion typed confirmation of "EXCLUDE" (per ADR-010). Uppercase, single word, memorable. Any objection?
10. **Draw cancellation surface (not designed here).** Post-commit cancellation is a real thing that will happen; it's not in this wireframe but I'll flag it for a future wireframe. Adaeze — what's the copy + audit expectation for a cancelled draw (refunds, communication to entrants, published cancellation event)?

### For 💻 Amelia:

11. **Draft persistence.** Draft draws sit in a `draft_draws` table server-side; auto-save on field blur PATCHes them. Discarded drafts are hard-deleted after 24 hours. Confirm this shape fits the module design.
12. **Idempotency on commit (§6.3).** `Idempotency-Key: {draft_id}` on `POST /admin/draws`. Same draft_id → same commitment on retry (server returns the original commit response). This is critical — a network stutter must not create a second draw with a different commitment.
13. **DrawCardPreview component reuse.** The review-step preview (§5.2) renders using the same `DrawCard` component the consumer uses. This is a design principle (surface parity) and a build principle (single source of truth). Confirm the component boundary supports this.
14. **Commitment receipt JSON schema.** Fields: `draw_id`, `commitment_hash` (full 64-char hex), `committed_at` (ISO-8601), `sales_open`, `sales_close`, `reveal_time`, `published_urls` (array), `audit_log_event_id`. Confirm — this becomes a small public schema.

### For 🏗️ Winston:

15. **DRAW-2026-07-08-A ID format.** Human-readable draw IDs (date + suffix) vs opaque UUIDs. Recommend human-readable for operator surfaces + audit log; UUIDs are ugly and unmemorable for operator recall. Confirm the URL structure and the ID scheme fit into the draw-engine module design.

---

## 10. Cross-references

- Flow source: `v0.5-demo-plan.md §2` (step 9).
- Upstream shell: `08-admin-login.md §1`.
- Downstream: `10-transcribe-free-entry.md` (Day 9), `11-close-and-reveal-draw.md` (Day 9), `13-audit-log-admin.md` (Day 10 — where the `draw.committed` event lives).
- Consumer counterpart: the draw card rendered on Screen 9.3 preview and appearing on `02-browse-active-draw.md`.
- Compliance flag: REVIEW-001 §3.1 (skill-question pool demo-only) — surfaced structurally as the WarningNote on Screen 9.2.
- Tokens: `tokens.md`.
- Tone: `tone-doc.md` — admin surface inherits the palette + typography; density is different, tone is not.
- ADRs: **ADR-006 (commit-reveal — this screen's entire reason to exist)**, ADR-003 (money-integer discipline on cash amount), ADR-004 (idempotency on publish), ADR-005 (audit-log event on commit), ADR-009 (RBAC — V0.5 two-role simplification per plan §3).

---

🎨 *End of wireframe 09.*

*Day 8 delivery complete: wireframes 08 (admin login + admin shell) and 09 (create draw — the commit action). This is where the operator's first action produces the first cryptographic artefact of the trust story. Day 9 tomorrow covers wireframes 10 (transcribe free entry), 11 (close draw), 12 (reveal draw). Adaeze wants an early look at wf-10 given the free-route parity invariant she flagged.*

# Wireframe 01 — Register → OTP → Password → Logged In

**Drafted:** 2026-07-08 (Day 3 per `tone-doc.md §8`)
**Amended:** 2026-07-08 (Day 7 per `tone-doc.md §8`) — DOB + 18+ hard-stop added at Screen 1.1 per `docs/compliance/reviews/REVIEW-001` §5.1 (Adaeze). Under-18 detection at registration prevents an unlawful ticket sale that would otherwise be caught only at the winner-claim gate. Change is bounded to Screen 1.1 layout, copy, and validation; downstream screens unchanged.
**Drafted by:** 🎨 Sally (BMad UX Designer)
**Status:** Draft — pending founder review at end of Week 1.
**Covers:** Flagship flow step 1 from `v0.5-demo-plan.md §2` — *"Register — email + phone → OTP (from Mailhog) → password → logged in."*
**Surface:** Flutter consumer app (iOS sim / Android / web build).
**Pairs with:** `tokens.md`, `tone-doc.md`, `v0.5-demo-plan.md`, `docs/compliance/reviews/REVIEW-001-v0.5-consumer-wireframes.md`.

---

## 0. Why this flow, first

The very first thing our user does on Atlas is register. Before she has seen a prize, before she has any evidence that Atlas is real, she is being asked for her email, her phone number, and (moments later) a password. This is the highest-friction moment in the product *and* the moment where the trust question — *"how do I know this is real?"* — is at its loudest.

**Every design decision below serves that question.** Not "how do we make this fast" — fast comes second. First: how do we make her feel that the thing she is signing up for is worth the friction, and that the friction itself is proof of seriousness (real product, real security, real operator) rather than proof of extraction (form-farm, data-harvest, WhatsApp giveaway scam)?

**Non-goals for V0.5:**
- Social login (Google/Apple). V1 concern; V0.5 is email + phone only.
- Biometric unlock. V1.
- Referral codes at registration. Reserved for V1 growth work.

---

## 1. Flow overview

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  Screen 1.1  │─────▶│  Screen 1.2  │─────▶│  Screen 1.3  │─────▶│  Screen 1.4  │
│  Register    │      │  OTP entry   │      │  Create pwd  │      │  Welcome     │
│  email +     │      │  (6-digit)   │      │  (single fld)│      │  (brief 1sec │
│   phone      │      │              │      │              │      │  splash then │
│              │      │              │      │              │      │  home)       │
└──────────────┘      └──────────────┘      └──────────────┘      └──────────────┘
       │                     │                     │
       │                     │                     │
       ▼                     ▼                     ▼
   (validate)         (validate OTP           (validate pwd
   phone/email        + 60s resend            complexity —
   → send OTP)        cooldown)               real-time)
```

4 screens. Each does one thing. No screen asks for more than it needs at the moment it needs it. This is the Alan Cooper "goal-directed" cut: registration is a goal, not a form.

**Why not one long form?** Because the OTP has to be issued between email/phone and password creation (that's the real-world sequencing), and because a wall of five fields on screen 1 destroys the "we treat you like an adult" feeling that Kuda solved (Anchor 4). We ask what we need, when we need it, and we explain why.

---

## 2. Screen 1.1 — Register (email + phone)

### 2.1 Layout (Flutter — mobile portrait, 375pt reference width)

```
┌─────────────────────────────────────────┐
│                                         │  ← status bar (system)
│  ← Back                                 │  ← top bar, 56pt, transparent
│                                         │
│                                         │  space.1200 (48pt)
│                                         │
│  ┌─┐                                    │
│  │ │  Atlas                             │  ← brand wordmark, Fraunces 24pt, navy
│  └─┘                                    │
│                                         │  space.800 (32pt)
│                                         │
│  Create an account                      │  ← type.display.section (40pt Fraunces)
│                                         │
│  We'll send a one-time code to your     │  ← type.body.default (16pt Inter)
│  phone. Takes about a minute.           │      color.text.secondary
│                                         │
│                                         │  space.800 (32pt)
│                                         │
│  Email                                  │  ← type.label.micro (12pt uppercase)
│  ┌─────────────────────────────────┐   │
│  │ you@domain.com                  │   │  ← input, 48pt tall, radius.small
│  └─────────────────────────────────┘   │
│                                         │  space.400 (16pt)
│  Phone (Nigerian mobile)                │  ← type.label.micro
│  ┌───┬─────────────────────────────┐   │
│  │+234│ 803 000 0000               │   │  ← input, dial-code chip is fixed
│  └───┴─────────────────────────────┘   │
│                                         │  space.400 (16pt)
│  Date of birth                          │  ← type.label.micro
│  ┌─────────────────────────────────┐   │
│  │ 12 / 03 / 1993                  │   │  ← native date picker, 48pt tall
│  └─────────────────────────────────┘   │      radius.small
│  You must be 18 or over to use Atlas.   │  ← body.small, secondary
│                                         │      (helper text, always visible —
│                                         │       the age gate is stated up-front,
│                                         │       not sprung as a validation error)
│                                         │
│                                         │  space.600 (24pt)
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  ✓  I agree to the Terms and    │   │  ← checkbox, unchecked by default
│  │     Privacy Notice              │   │      "Terms" and "Privacy Notice"
│  └─────────────────────────────────┘   │      are inline links (navy underline)
│                                         │
│                                         │  space.800 (32pt)
│                                         │
│  ┌─────────────────────────────────┐   │
│  │           Continue              │   │  ← primary button, 52pt tall
│  └─────────────────────────────────┘   │      radius.medium, brand.primary bg
│                                         │      text.inverted, type.body.button
│                                         │
│                                         │  space.400 (16pt)
│                                         │
│  Already have an account? Sign in       │  ← type.body.small, centered
│                                         │      "Sign in" is inline link (navy)
│                                         │
│                                         │  bottom safe-area padding
└─────────────────────────────────────────┘
```

### 2.2 Components used

From the V0.5 mini design system (component specs land Day 13):

- `TopBar` — back-arrow variant, transparent background.
- `BrandMark` — small wordmark variant.
- `TextInput` — email variant (autocorrect off, keyboard type email).
- `PhoneInput` — dial-code chip + numeric input (V0.5: Nigerian `+234` fixed; V1 introduces country picker).
- `DateInput` — native date picker, initial value set to 30 years ago per wireframe 07 §4.4.
- `Checkbox` — label with inline links.
- `Button` — primary variant, full width.
- `InlineLink` — used inside checkbox label and bottom row.

### 2.3 States

**Default:** as drawn. Continue button is *disabled* until: email is well-formed, phone is 10 digits post-dial-code, DOB is set and computes ≥ 18 years today, checkbox is checked. Disabled state uses `color.surface.elevated` background + `color.text.secondary` text — clearly non-interactive, not greyed to the point of invisibility.

**Field-level validation (real-time, on blur):**
- Email malformed → below field: `Check the email — it needs an @ and a domain.` in `color.state.danger` at `type.body.small`.
- Phone < 10 digits → below field: `Nigerian mobile numbers have 10 digits after +234.`
- Phone not starting with 7, 8, or 9 → below field: `Check the number — Nigerian mobiles start with 7, 8, or 9.`
- DOB under 18 (computed against today) → helper-text row swaps from `color.text.secondary` to `color.state.danger` and copy becomes: `You must be 18 or over to use Atlas. Contact us if there's been a mistake.` — with `Contact us` as an inline link opening a mailto sheet. Continue button stays disabled. Copy is deliberately consistent with the wireframe 07 §4.3 age-gate wording, so users who encounter the same block on the claim path recognise the same voice.
- DOB not set → Continue disabled; no explicit error until the user tries to interact past the field.

**Continue button pressed but form invalid:** button remains disabled — no error toast, no shake. The disabled state itself is the feedback.

**Continue button pressed, form valid:**
1. Button label changes to "Sending code…" and shows an inline spinner (right-aligned, 16pt).
2. Button becomes non-interactive.
3. Network request fires. Timeout: 15 seconds.
4. On success → navigate to screen 1.2 with an `SlideRight` transition (250ms, ease-out).
5. On failure → button reverts to "Continue", top-of-screen error banner appears:

  > We couldn't send the code. Check your connection and try again.

  Banner uses `color.state.danger` at 12% opacity as background, `color.state.danger` for text, 4pt left border in solid `state.danger`. Dismissable via right-side X.

**Loading:** covered above. No full-screen loader for this action.

**Empty state:** N/A (screen is always populated).

### 2.4 Copy (final)

| Element | Copy |
|---|---|
| Page headline | Create an account |
| Subhead | We'll send a one-time code to your phone. Takes about a minute. |
| Email label | Email |
| Email placeholder | you@domain.com |
| Phone label | Phone (Nigerian mobile) |
| Phone placeholder | 803 000 0000 |
| DOB label | Date of birth |
| DOB helper (default) | You must be 18 or over to use Atlas. |
| DOB helper (under 18) | You must be 18 or over to use Atlas. **Contact us** if there's been a mistake. |
| Consent | I agree to the Terms and Privacy Notice |
| Consent (Terms link) | Terms → opens sheet with `_bmad-output/planning-artifacts/legal/` T&C draft |
| Consent (Privacy link) | Privacy Notice → opens sheet with privacy notice |
| Primary CTA (default) | Continue |
| Primary CTA (loading) | Sending code… |
| Sign-in link | Already have an account? **Sign in** |
| Error banner (send failed) | We couldn't send the code. Check your connection and try again. |

Copy rules honoured: no exclamation marks, no "hurry", no "amazing", second person, short sentences.

### 2.5 Accessibility notes

- **Focus order:** Back arrow → Email input → Phone input → DOB input → Terms checkbox → Continue button → Sign-in link. Standard reading order; no skip links needed at this screen size.
- **ARIA / semantics (web build):** `<main>` wrapping content; `<h1>` for page headline; inputs use `<label>` associations (not placeholder-as-label); button has `aria-describedby` pointing at any field-level error present.
- **Screen reader announcements:** on field blur validation error, error text is announced via `aria-live="polite"` region below the field. On send failure, banner is `aria-live="assertive"`.
- **Contrast:** all pairings verified against tokens (`text.primary` on `surface.base` = 16:1; button label `text.inverted` on `brand.primary` = 14.8:1). Disabled button state (`text.secondary` on `surface.elevated`) = 5.6:1 → still readable per WCAG.
- **Touch targets:** all interactive elements ≥ 44×44pt. Continue button is 52pt tall × full-width. Checkbox tap target includes the label (48pt tall).
- **Keyboard (web build):** Enter in either input submits if form is valid; Tab cycles per focus order; Escape does nothing at this screen (no destructive action to undo).
- **Autofill:** email input has `autocomplete="email"`; phone has `autocomplete="tel-national"`; DOB has `autocomplete="bday"`. All marked `inputmode` appropriately.
- **DOB helper text** (`aria-describedby` on the field) is announced with the field on focus. When the field enters the under-18 danger state, the helper text is announced via `aria-live="polite"` on the next change, and the field itself gains `aria-invalid="true"`.
- **Reduce motion:** if user has reduce-motion preference, screen transition to 1.2 is fade only (200ms), not slide.

### 2.6 Interaction notes

- **Back arrow:** navigates to previous screen. If registration was entered from the marketing splash, returns there. If entered from "Sign in → Create account", returns to sign in.
- **On Continue success:** phone number and email are held in a scoped in-memory registration state (not persisted to disk until account is actually created at end of screen 1.3). If the user backgrounds the app between 1.2 and 1.3, the state survives up to 10 minutes; after 10 minutes, registration restarts from 1.1.
- **Terms / Privacy links:** open as a modal bottom sheet (Flutter `showModalBottomSheet`), not a full navigation. Sheet has an "I've read this" close action but does NOT toggle the checkbox — user must return and explicitly tick. This intentional friction matches the "we treat you like an adult" posture.
- **What happens if user submits the same email twice?** V0.5 behaviour: backend returns 409 Conflict; banner shows *"That email is already registered. Sign in instead?"* with an inline link. No account enumeration mitigation in V0.5 (documented as a known V1 hardening ticket per `v0.5-demo-plan.md §3`).
- **DOB is captured client-side but must be re-validated server-side on the `POST /users` request.** Client-side age computation prevents accidental capture; server-side re-validation prevents deliberate bypass. If server rejects because of age (client thought ≥18 but server disagrees — e.g. locale-string edge case), Continue reverts and the DOB field enters the danger state with the same copy.
- **DOB reuse.** The value captured here is the authoritative DOB for the account; wireframe 07 §4.1 (personal details step of the winner claim) pre-fills DOB from the account and marks it read-only. Winners cannot change their DOB during a claim; if there's a mistake, they contact support before submitting a claim.

---

## 3. Screen 1.2 — OTP entry

### 3.1 Layout

```
┌─────────────────────────────────────────┐
│                                         │
│  ← Back                                 │
│                                         │
│                                         │  space.1200
│                                         │
│  Enter the code                         │  ← type.display.section
│                                         │
│  Sent to +234 803 000 0000              │  ← type.body.default, secondary
│  Not you? Change number                 │  ← inline link, navy
│                                         │
│                                         │  space.800
│                                         │
│  ┌───┐┌───┐┌───┐┌───┐┌───┐┌───┐       │  ← 6 digit boxes, 48pt square
│  │   ││   ││   ││   ││   ││   │        │      radius.small, hairline border
│  └───┘└───┘└───┘└───┘└───┘└───┘       │      auto-focus first on mount
│                                         │
│                                         │  space.600
│                                         │
│  Didn't get it? Resend in 47s           │  ← body.small, secondary
│                                         │      "Resend" becomes link after 60s
│                                         │
│                                         │  space.1200
│                                         │
│  (Continue button appears when          │
│   6 digits entered — same styling       │
│   as screen 1.1)                        │
│                                         │
└─────────────────────────────────────────┘
```

### 3.2 Components

- `TopBar` (back variant)
- `OtpInput` — 6-digit segmented input. New component; spec written Day 13.
- `Button` (primary, but only rendered when input is complete — see interactions)
- `InlineLink` (× 2 — "Change number" and "Resend")

### 3.3 States

**Default (just landed):** digit boxes empty, first has focus + input caret, keyboard is up (numeric). Resend countdown at 60s. Continue button is **not rendered** until 6 digits entered — this is deliberate; the screen resolves itself.

**Digits entering:** as each digit typed, cursor advances to next box. Boxes fill with `type.display.card` sized digits (24pt Fraunces), `color.text.primary`.

**Incorrect OTP (server validated):** boxes flash `color.state.danger` border for 400ms, then clear. Cursor returns to first box. Field-level error below input:

> That code isn't right. Try again, or resend.

If user has entered 3 wrong codes in a row, add: *"Resend if you'd like a fresh code."* Do not lock the account in V0.5.

**Correct OTP:** boxes turn `color.state.success` for 300ms, then screen navigates to 1.3.

**Resend countdown active (60s):** "Resend in Ns" — greyed out, not a link.
**Resend available:** "Didn't get it? **Resend**" — link is active. On tap: countdown resets, toast confirms *"New code sent."*

**Change number:** returns to screen 1.1 with fields prefilled (email retained). No OTP is invalidated server-side in V0.5 (documented shortcut).

**Loading (verify request in flight):** boxes non-editable, faint spinner overlays digit row. Typical <500ms; no visible spinner if response < 200ms.

### 3.4 Copy

| Element | Copy |
|---|---|
| Headline | Enter the code |
| Sent-to line | Sent to +234 803 000 0000 |
| Change link | Not you? **Change number** |
| Resend (waiting) | Didn't get it? Resend in {n}s |
| Resend (available) | Didn't get it? **Resend** |
| Toast after resend | New code sent. |
| Error (wrong) | That code isn't right. Try again, or resend. |
| Error (wrong ×3) | That code isn't right. Try again, or **resend** if you'd like a fresh one. |
| Loading spinner | (no label) |

### 3.5 Accessibility notes

- **OTP paste handling (critical):** if user long-presses first box and pastes a 6-digit string, all boxes populate in order. This is essential — SMS autofill and clipboard paste are the most common completion paths on mobile.
- **iOS SMS autofill:** input group is marked with `textContentType: .oneTimeCode` so iOS surfaces the code above the keyboard.
- **Android SMS autofill:** app uses SMS Retriever API; app hash appended to OTP SMS by backend.
- **Focus order:** Back → OTP group → Change link → Resend link.
- **Screen reader:** boxes announce as a single "one-time code, 6 digits" input rather than 6 separate fields. Progress is announced ("3 of 6 entered") on each digit.
- **Digit boxes on failure:** the flash is accompanied by an `aria-live="assertive"` announcement of the error text — colour is never the sole failure indicator.
- **Countdown:** announced only on completion ("You can now resend the code"), not every second — otherwise it drowns everything else out.

### 3.6 Interaction notes

- **On mount:** first box focused, keyboard up. If a code is already in clipboard (matches `^\d{6}$`), do NOT auto-paste — offer a subtle "Paste code from clipboard" chip above the input group. Auto-paste feels intrusive.
- **On 6th digit entered:** immediately fire verify request (do not wait for Continue tap). Continue button appears at bottom for one-thumb users who prefer explicit submit, but the request has already fired.
- **Backspace on empty box:** moves focus to previous box and clears its digit.
- **Timer:** 60-second cooldown per resend. After 3 resends without a successful verify, "Resend" becomes disabled with helper text *"If codes aren't arriving, check the phone number or contact support."* Contact support opens the WhatsApp shortcut (or, in V0.5, the mailto: since WA is stubbed).

---

## 4. Screen 1.3 — Create password

### 4.1 Layout

```
┌─────────────────────────────────────────┐
│                                         │
│  ← Back                                 │
│                                         │
│                                         │  space.1200
│                                         │
│  One more step                          │  ← display.section
│                                         │
│  Set a password. You'll use this to     │  ← body.default, secondary
│  sign back in on any device.            │
│                                         │
│                                         │  space.800
│                                         │
│  Password                               │  ← label.micro
│  ┌─────────────────────────────────┐   │
│  │ ●●●●●●●●                     👁 │   │  ← password input, show/hide toggle
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ ○ 10 characters or more         │   │
│  │ ○ Mix of letters and numbers    │   │  ← rules checklist, live-updates
│  │ ○ Not one you use for banking   │   │      as user types. Circle → check.
│  └─────────────────────────────────┘   │
│                                         │
│                                         │  space.800
│                                         │
│  ┌─────────────────────────────────┐   │
│  │        Create account           │   │  ← primary button
│  └─────────────────────────────────┘   │
│                                         │
│                                         │  space.400
│                                         │
│  By creating your account you accept    │  ← body.small, centered, secondary
│  the Terms and Privacy Notice.          │      re-affirmation of consent
│                                         │
└─────────────────────────────────────────┘
```

### 4.2 Components

- `TopBar` (back)
- `PasswordInput` — with show/hide toggle (eye icon).
- `RulesChecklist` — new component; renders array of {label, satisfied: bool}. Circles turn to `state.success` checks live.
- `Button` (primary)

### 4.3 States

**Default:** password field empty, all three rules unmet (empty circles in `text.secondary`). Create-account button disabled.

**Typing:** rules light up in real-time as each is satisfied. When all three met, button enables.

**Show password:** eye-icon toggle; input `obscureText` flips. Show state auto-reverts to hidden after 5 seconds if the user hasn't tapped Create.

**Create pressed (loading):** button label → "Creating account…" + inline spinner. Request fires.

**Success:** navigate to screen 1.4 with `Fade` transition (300ms).

**Failure (network):** banner *"We couldn't create the account. Try again in a moment."* — password field NOT cleared.

**Failure (server validation — e.g. compromised password blocklist, if V1 enforces one — V0.5 skips):** N/A for V0.5.

### 4.4 Copy

| Element | Copy |
|---|---|
| Headline | One more step |
| Subhead | Set a password. You'll use this to sign back in on any device. |
| Password label | Password |
| Rule 1 | 10 characters or more |
| Rule 2 | Mix of letters and numbers |
| Rule 3 | Not one you use for banking |
| Primary CTA (default) | Create account |
| Primary CTA (loading) | Creating account… |
| Consent re-affirm | By creating your account you accept the Terms and Privacy Notice. |
| Error banner | We couldn't create the account. Try again in a moment. |

**Note on Rule 3.** *"Not one you use for banking"* is unusual — it cannot be programmatically enforced. It is deliberately advisory. This is Atlas taking a stance: we don't want you to reuse a password that, if we were ever breached, could open your bank account. The rule is a **piece of tone** as much as a piece of security guidance. If founder objects, alternatives: drop it (weakest — misses a trust-story moment), or replace with *"Not a password you've used before on another site"* (also unenforceable but more conventional). Recommend keeping.

### 4.5 Accessibility notes

- Password field marked `autocomplete="new-password"` so password managers offer to generate/save.
- Rules checklist has `role="list"` with each item `role="listitem"`; satisfaction state announced via `aria-live="polite"` when it changes ("Rule met: 10 characters or more").
- Show/hide toggle has `aria-label="Show password"` / `"Hide password"` and is keyboard-reachable.
- Field is min 48pt tall.

### 4.6 Interaction notes

- **Password strength meter?** Explicitly no. Meters give false confidence and are noise. The three rules are the guidance.
- **On success:** email + hashed password are POSTed with the previously-verified OTP session token. Account is created server-side. Session token is returned; app stores it in secure storage (Flutter `flutter_secure_storage`).
- **What if the user backs out of screen 1.3?** State is preserved for 10 min per screen 1.1 rules. Backing out fully (out of the flow) discards.

---

## 5. Screen 1.4 — Welcome (brief)

### 5.1 Layout

```
┌─────────────────────────────────────────┐
│                                         │
│                                         │  space.2400
│                                         │
│                                         │
│              ✓                          │  ← 64pt gold check-in-circle
│                                         │      color.brand.accent
│                                         │
│         You're in.                      │  ← display.section, centered
│                                         │
│    Loading your account…                │  ← body.default, centered, secondary
│                                         │
│                                         │
│                                         │
└─────────────────────────────────────────┘
```

### 5.2 Components

- `SplashCheck` — one-off component (gold check + label + subtext). Not reused; spec is inline in this wireframe.

### 5.3 States

**Only state.** Screen visible for 800ms – 1200ms, then auto-navigates to the home / active draw browse (flagship flow step 2).

If the follow-up navigation fails (rare), fallback to a manual "Continue to Atlas" button after 3s.

### 5.4 Copy

| Element | Copy |
|---|---|
| Headline | You're in. |
| Subtext | Loading your account… |
| Fallback button | Continue to Atlas |

**Design intent:** *"You're in."* is deliberately understated. Compare to what a game-show product would ship (*"Welcome to Atlas! Get ready to WIN BIG!"*). Understatement is the trust posture. The gold check is the celebration; the copy is the calm.

### 5.5 Accessibility

- Screen announces *"You're in. Loading your account."* on mount, via `aria-live="assertive"`.
- Reduce-motion: no check-in animation; check appears solid.

### 5.6 Interaction

- No user interaction expected. This is a bridge, not a destination.

---

## 6. Cross-flow notes

- **Backend behaviour assumed (Amelia to confirm in Week 3 identity module):** OTP is 6-digit numeric, single-use, TTL 10 minutes, resend rate-limited to 1/60s + 3/hour per phone.
- **OTP delivery in V0.5:** SMS is stubbed — the code is delivered to Mailhog as an email `To: +234...@sms-mock.local`. The founder demoing sees the code in Mailhog UI. For the investor demo this is fine (documented in `v0.5-demo-plan.md §4`).
- **What "logged in" means:** session token in secure storage; user can now enter the paid-ticket flow (flagship step 4) which is where the trust story really starts to earn.

---

## 7. Open questions for founder review

Small list. Each is a stance that can shift without a re-sweep:

1. **Rule 3 (*"Not one you use for banking"*) on the password screen** — keep as tone-carrying, drop, or replace? Recommend keep. (See §4.4.)
2. **Consent checkbox on screen 1.1** — currently one checkbox for both Terms and Privacy. NDPA guidance (per counsel-engagement-brief.md) may require separate consent for personal data processing vs T&C. V0.5 acceptable to bundle; V1 will need separation. Flag for Adaeze's review.
3. **"Continue to Atlas" fallback on 1.4** — is 3 seconds the right threshold? Could be 2. Any longer and the user starts to doubt.
4. **No social login in V0.5** — confirmed OK for demo? A "Continue with Google" button dramatically shortens registration but adds a Google Cloud dependency I've explicitly kept out of V0.5. If you want it back in scope for the demo, flag now.

---

## 8. Cross-references

- Flow source: `v0.5-demo-plan.md §2` (step 1).
- Tokens: `tokens.md` (all colours, spacing, radii, elevation, type).
- Tone: `tone-doc.md` (voice, copy rules, Nigerian cultural context).
- Compliance (consent copy): to be reviewed by ⚖️ Adaeze per `docs/AINE-AGENTS.md`.
- Backend contract (identity module): TBD Week 3 — 💻 Amelia.

---

🎨 *End of wireframe 01. Next up (Day 4): browse active draw + free-entry disclosure. Push back on open questions in §7 before Day 4 begins.*

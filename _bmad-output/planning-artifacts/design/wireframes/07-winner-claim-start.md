# Wireframe 07 — Winner Claim Start

**Drafted:** 2026-07-08 (Day 6 per `tone-doc.md §8`)
**Amended:** 2026-07-08 (Day 7 per `tone-doc.md §8`) — five compliance amendments per `docs/compliance/reviews/REVIEW-001` (Adaeze): (a) BVN help copy now discloses the self-exclusion purpose (§5.3, per REVIEW-001 §5.2); (b) accepted-ID list drops Voter's card and promotes NIN as primary (§5.3, per REVIEW-001 §5.3); (c) §7.5 consent bundle replaced with two-required + one-optional checkbox pattern (per REVIEW-001 §5.5 + §4.3 winner-name publication consent); (d) four rejected-claim state variants drafted by Adaeze added to §8.3 (per REVIEW-001 §5.6); (e) DOB field on §4.1 becomes read-only pre-fill from registration (per REVIEW-001 §5.1 + wf-01 amendment). SLA copy *"usually within 1 working day"* on §8.4 flagged as rejected for real-user launch — retained for V0.5 demo only per REVIEW-001 §5.7.
**Drafted by:** 🎨 Sally (BMad UX Designer)
**Status:** Draft — Adaeze approved with conditions on 2026-07-08 (REVIEW-001), all conditions applied. Founder review pending Week 1 exit. **For real-user launch: SLA copy must switch to conservative wording (§8.4 note); ID-image retention policy is a Phase 3 gap owned jointly by Adaeze + Tobi.**
**Covers:** Flagship flow step 7 from `v0.5-demo-plan.md §2` — *"Winner claim start — if won, tap 'Claim' → prize claim form → submit → status shows 'claim received.'"*
**Surface:** Flutter consumer app.
**Pairs with:** `05-my-tickets.md`, `06-draw-completes-notification.md` (upstream), `tokens.md`, `tone-doc.md`, `docs/compliance/reviews/REVIEW-001-v0.5-consumer-wireframes.md`. Operator-side of the claim (review + approve) is a future wireframe (Day 8+, part of admin flows in Week 2 — not currently scheduled in the design pass; will be picked up if operator claim flow is in V0.5 scope beyond a stub).

---

## 0. Why this flow gets careful handling

The winner claim is the emotional peak — but it's also the moment where trust is either cemented or squandered. She has just been told she won ₦2,000,000. What she does next determines whether she gets it.

Two design tensions to hold:

1. **Bentley delivery vs KYC form.** Tone-doc.md §1 says winner claim pages feel closer to a Bentley delivery experience than a Publishers Clearing House cheque handover. But the operational reality is: this is a KYC-heavy form (BVN, government ID, bank account details, tax attestations later). Making a KYC form feel like a Bentley delivery is the design job. The way to do it is *not* to hide the friction — it's to make each step feel considered, explained, respectful.

2. **Speed vs care.** She wants her money. She also wants it done right. The temptation is to add "You could have it by tomorrow!" urgency. That's a Publishers Clearing House move. Atlas's promise is *"paid within 5 working days"* — not fast, not slow, considered. The claim flow should feel like *the money is safe and coming*, not *hurry up and finish the form*.

**Non-goals for V0.5:**
- Actual KYC vendor integration. Per plan §3, V0.5 uses `ManualApproveStub` — the operator manually approves the claim in the admin. The consumer surface captures the data; the enforcement is admin-side.
- Real payout initiation. V0.5 operator marks claim as "approved for payout"; actual bank transfer is out of scope. Copy makes no false promise about *when* the payment lands, only about the process.
- Physical prize delivery (car, house). V0.5 seed prize is cash. Physical-prize claim flows are V1+ (require different fields — delivery address, collection appointment, etc.). The claim form here is cash-only.
- Multi-jurisdiction bank details. V0.5 is Nigerian bank accounts only.
- Tax handling. V1 — will need withholding-tax disclosure once we understand the treatment.

---

## 1. Flow overview

```
                        (from wireframe 06 §3
                         "Claim your prize"
                         or wireframe 05 §2.5
                         winning ticket CTA)
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │  Screen 7.1          │
                        │  Claim intro         │
                        │  what you'll need,   │
                        │  what happens,       │
                        │  our commitment      │
                        └──────────┬───────────┘
                                   │ Start claim
                                   ▼
                        ┌──────────────────────┐
                        │  Screen 7.2          │
                        │  Personal details    │
                        │  full name, DOB,     │
                        │  address             │
                        └──────────┬───────────┘
                                   │ Next
                                   ▼
                        ┌──────────────────────┐
                        │  Screen 7.3          │
                        │  Identity            │
                        │  BVN + ID upload     │
                        └──────────┬───────────┘
                                   │ Next
                                   ▼
                        ┌──────────────────────┐
                        │  Screen 7.4          │
                        │  Payout details      │
                        │  bank account        │
                        └──────────┬───────────┘
                                   │ Next
                                   ▼
                        ┌──────────────────────┐
                        │  Screen 7.5          │
                        │  Review + submit     │
                        │  everything on one   │
                        │  page, edit chips    │
                        └──────────┬───────────┘
                                   │ Submit claim
                                   ▼
                        ┌──────────────────────┐
                        │  Screen 7.6          │
                        │  Claim received      │
                        │  status + timeline   │
                        └──────────────────────┘
```

Six screens. One intro + four form steps + one confirmation. **Progress indicator** appears above the form steps so the user knows where she is. The intro and the confirmation don't need progress — they're bookends.

**Why a stepped form rather than one long form?** Because the fields require *different kinds of attention*: personal details are self-knowledge (easy), identity involves finding your BVN and a photo of your ID (harder — often means leaving the app), payout is data-entry (moderate — requires being at your bank app). A step-per-context lets her pause and resume at natural boundaries. It also lets us validate a step before moving on, so a failed BVN doesn't invalidate the whole form.

---

## 2. Screen 7.1 — Claim intro

### 2.1 Layout

```
┌─────────────────────────────────────────┐
│                                         │
│  ← Back                                 │
│                                         │
│                                         │  space.800
│                                         │
│  ▪ WINNER — TICKET 04829                 │  ← type.label.micro gold uppercase
│                                         │
│                                         │  space.400
│                                         │
│  Let's get you paid.                    │  ← type.display.section (40pt Fraunces)
│                                         │      text.primary
│                                         │
│                                         │  space.400
│                                         │
│  ₦2,000,000 in cash, paid to your       │  ← body.default, primary
│  Nigerian bank account within           │
│  5 working days of a completed claim.   │
│                                         │
│                                         │  space.800
│                                         │
│  What you'll need                       │  ← type.display.card
│                                         │
│                                         │  space.400
│                                         │
│  ┌───────────────────────────────────┐ │  ← RequirementCard, radius.large,
│  │  1  Your name as it appears        │ │      surface.elevated, hairline border,
│  │     on your ID                     │ │      elevation.0, 20pt padding.
│  │                                    │ │      3 stacked cards, one per requirement
│  │  2  Your Bank Verification         │ │
│  │     Number (BVN)                   │ │
│  │                                    │ │
│  │  3  A photo of a government-       │ │
│  │     issued ID (NIN slip, driver's  │ │
│  │     licence, or international      │ │
│  │     passport)                      │ │
│  │                                    │ │
│  │  4  A Nigerian bank account in     │ │
│  │     your legal name                │ │
│  └───────────────────────────────────┘ │
│                                         │
│                                         │  space.800
│                                         │
│  What happens next                      │  ← type.display.card
│                                         │
│                                         │  space.400
│                                         │
│  1. You submit these details.           │  ← numbered list, body.default
│  2. Our team reviews the claim          │      (usually within 1 working day).
│  3. We confirm your bank account        │
│     matches your BVN.                   │
│  4. Payment is sent to your account.    │
│  5. You'll receive an email with the    │
│     payment reference.                  │
│                                         │
│                                         │  space.800
│                                         │
│  ┌───────────────────────────────────┐ │
│  │           Start claim              │ │  ← primary button, navy fill
│  └───────────────────────────────────┘ │
│                                         │
│                                         │  space.400
│                                         │
│  I'll come back later                   │  ← inline link, centered secondary
│                                         │
│                                         │  bottom safe area
└─────────────────────────────────────────┘
```

### 2.2 Components used

- `TopBar` (back).
- `SectionLabel` — gold eyebrow, this time carrying the ticket number as context.
- `PageHeadline` (display.section).
- `RequirementCard` — new; single card containing a numbered list of items. Used only here (the "what you'll need" pattern).
- `SectionHeadline` — "What happens next".
- `NumberedList` — reused from wireframe 03 §3.2.
- `Button` (primary).
- `InlineLink` — "I'll come back later" (secondary tone; saves progress and returns to My tickets).

### 2.3 States

**Default:** as drawn.

**Resuming a partial claim:** headline changes to *"Let's finish your claim."* Below the RequirementCard, an additional line: *"You started on {date}. Everything you've entered is saved."*

**Claim already submitted (user re-lands here from a ticket detail):** page becomes a redirect to screen 7.6 (status).

**Claim already paid:** page becomes a redirect to a "Payment sent" variant of screen 7.6.

### 2.4 Copy

| Element | Copy |
|---|---|
| Eyebrow | WINNER — TICKET {number} |
| Headline | Let's get you paid. |
| Subhead | ₦{amount} in cash, paid to your Nigerian bank account within 5 working days of a completed claim. |
| Requirements headline | What you'll need |
| Req 1 | Your name as it appears on your ID |
| Req 2 | Your Bank Verification Number (BVN) |
| Req 3 | A photo of a government-issued ID (NIN slip, driver's licence, or international passport) |
| Req 4 | A Nigerian bank account in your legal name |
| Next-steps headline | What happens next |
| Step 1 | You submit these details. |
| Step 2 | Our team reviews the claim (usually within 1 working day). |
| Step 3 | We confirm your bank account matches your BVN. |
| Step 4 | Payment is sent to your account. |
| Step 5 | You'll receive an email with the payment reference. |
| Primary CTA | Start claim |
| Save-and-leave link | I'll come back later |
| Resume subhead | You started on {date}. Everything you've entered is saved. |

**Copy commentary:**

- *"Let's get you paid."* is a specific tone choice. Alternatives considered and rejected: *"Congratulations, winner!"* (game-show), *"Prize claim form"* (bureaucratic), *"Time to collect your winnings"* (Publishers Clearing House). *"Let's get you paid."* is direct, respectful, and puts Atlas in a role of *helping her get her money*, not *making her prove she deserves it*.
- *"Within 5 working days of a **completed claim**"* — the "completed claim" qualifier is deliberately explicit. It signals: the countdown starts when the form is done, not when she started it. This is fair to Atlas and fair to her; it prevents a *"but I started 3 days ago!"* misunderstanding.
- *"Our team reviews the claim (usually within 1 working day)."* — the "usually" is important. We do not want to make a hard SLA promise here. If a claim needs deeper review (compliance flag, KYC mismatch), it takes longer. "Usually" is honest.
- The "What happens next" list ends with *"You'll receive an email with the payment reference."* — a closing beat. She knows exactly how she'll know it's done.

### 2.5 Accessibility

- **Focus order:** Back → Page headline → Requirements card (composite; each numbered item is a list item, group announced) → Next-steps headline + list → Start claim → I'll come back later.
- **Announcement on mount:** *"Winner. Ticket zero four eight two nine. Let's get you paid. Two million naira in cash, paid to your Nigerian bank account within five working days of a completed claim."*
- **Requirement card semantics:** `role="list"` with 4 `listitem` children. Each item read as *"one, your name as it appears on your ID"* etc.
- **Contrast:** all tokens as spec.
- **Reduce motion:** N/A (no motion here).

### 2.6 Interaction

- **Start claim:** navigates to screen 7.2 with a `SlideRight` transition (250ms).
- **I'll come back later:** saves state, navigates back to ticket detail (wireframe 05 §3). Ticket detail winning-variant primary CTA switches from *"Claim your prize"* to *"Continue your claim"*.
- **Back:** returns to reveal page (wireframe 06 §3) or ticket detail depending on entry point.

---

## 3. Form step architecture (shared across screens 7.2–7.4)

All three form-step screens share the same shell:

```
┌─────────────────────────────────────────┐
│                                         │
│  ← Back                    Save + close │  ← top bar
│                                         │
├─────────────────────────────────────────┤  ← hairline
│                                         │
│  ●●●○   Step 3 of 4                     │  ← ProgressIndicator (see §3.1)
│                                         │
├─────────────────────────────────────────┤  ← hairline
│                                         │
│                                         │  space.600
│                                         │
│  [Step headline — display.card]         │
│                                         │
│  [Optional context sentence —           │
│   body.default secondary]               │
│                                         │
│                                         │  space.800
│                                         │
│  [Fields — see per-screen §s below]     │
│                                         │
│                                         │  space.1200
│                                         │
│  ┌───────────────────────────────────┐ │
│  │              Next                  │ │  ← primary CTA, disabled until valid
│  └───────────────────────────────────┘ │
│                                         │
│                                         │  bottom safe area
└─────────────────────────────────────────┘
```

### 3.1 ProgressIndicator component

Four dots (one per form step). Filled = complete; hollow = incomplete; solid ring = current. Colour: brand.primary. Label alongside: *"Step {n} of 4"* in body.small secondary.

No percentage bar, no "You're 75% done!" — dots + label read as considered pace, not gamification.

### 3.2 Save + close

Trailing action in top bar. Saves current field values (whatever is valid) and returns to ticket detail. On return via *"Continue your claim"*, resumes at the step she left.

### 3.3 Field-level behaviour

- Fields validate on blur, not on every keystroke (except live rules like BVN length).
- Errors appear below the field in state.danger, body.small.
- Required fields are marked with a small `▪` bullet in `color.brand.accent` (gold) before the label. No red asterisks (fire-engine red is forbidden).
- Optional fields are labelled *"(optional)"* in `color.text.secondary` — never assumed.

---

## 4. Screen 7.2 — Personal details

### 4.1 Layout

Uses form step shell (§3). Content:

```
Step 1 of 4

Your details

The name below must match the name on
the ID you'll upload in the next step
and the bank account you'll add later.

┌───────────────────────────────────┐
│ ▪ Full legal name                 │
├───────────────────────────────────┤
│ Chinelo Okonkwo                   │
└───────────────────────────────────┘

┌───────────────────────────────────┐
│ ▪ Date of birth (from registration)│
├───────────────────────────────────┤
│ 12 / 03 / 1993        ✓ verified  │  ← read-only (DOB is captured at
└───────────────────────────────────┘      registration and 18+ verified there
                                          per wf-01 amendment 2026-07-08).
                                          Contact support to correct.

┌───────────────────────────────────┐
│ ▪ Phone (confirmed at registration)│
├───────────────────────────────────┤
│ +234 803 000 0000     ✓ verified  │  ← read-only, verified indicator
└───────────────────────────────────┘

┌───────────────────────────────────┐
│ ▪ Email (confirmed at registration)│
├───────────────────────────────────┤
│ chinelo@example.com   ✓ verified  │  ← read-only
└───────────────────────────────────┘

┌───────────────────────────────────┐
│ ▪ Home address                    │
├───────────────────────────────────┤
│ Line 1                            │
│ Line 2 (optional)                 │
│ City                              │
│ State           [Lagos       ▾]   │  ← dropdown, Nigerian states
└───────────────────────────────────┘

           [ Next ]
```

### 4.2 States

**Default (fresh):** phone, email, and DOB pre-filled from registration and read-only (DOB gained this treatment via wf-01 amendment 2026-07-08 per REVIEW-001 §5.1). All other fields empty. Next disabled.

**Default (resuming):** all previously-entered values pre-filled; validation state preserved.

**Field errors:**
- Full legal name empty → *"Enter the name that appears on your ID."*
- Name contains only one word → *"Enter both your given name and family name."*
- Date of birth < 18 years old → *"You must be 18 or over to claim a prize."* — with an escalation path (contact support) via inline link. **This is a hard-stop.**
- Address missing required fields → *"Complete your address so we can send payment records."*

**Loading (Next tapped):** button label *"Saving…"* + spinner. Saves current step values, advances to 7.3.

### 4.3 Copy

| Element | Copy |
|---|---|
| Step headline | Your details |
| Context | The name below must match the name on the ID you'll upload in the next step and the bank account you'll add later. |
| Field label — name | Full legal name |
| Field label — dob | Date of birth |
| Field label — phone | Phone (confirmed at registration) |
| Field label — email | Email (confirmed at registration) |
| Field label — address | Home address |
| Address sub-labels | Line 1 / Line 2 (optional) / City / State |
| Verified indicator | ✓ verified |
| Error — name empty | Enter the name that appears on your ID. |
| Error — name single word | Enter both your given name and family name. |
| Error — dob under 18 | You must be 18 or over to claim a prize. |
| Error — under-18 support link | Contact us if there's been a mistake. |
| CTA | Next |

**Copy commentary:**

- The context sentence at the top of the step matters: it tells her *why* the name is important before she types it, so the friction of getting it right feels reasonable, not arbitrary. Every step of a KYC-heavy form should explain the why of the friction; this pattern repeats on 7.3 and 7.4.
- Under-18 hard-stop: designed as a firm boundary. This is a regulatory line, not a UX line. Adaeze to confirm.

### 4.4 Accessibility

- Field labels are `<label>` associated (never placeholder-as-label).
- Verified indicator has `aria-label="Verified at registration"`.
- Date-of-birth uses native date picker; on Flutter, `showDatePicker` with initial date set to 30 years ago (median adult on the platform, statistical guess).
- State dropdown: filterable typeahead of Nigerian states.
- Error messages: `aria-live="polite"` per field.

### 4.5 Interaction

- **Autofill:** legal name → `name`, address lines → address autofill hints (Flutter `AutofillHints.streetAddressLevel1..3`).
- **Under-18 detection:** now enforced at registration (wf-01 amendment). This screen inherits a verified-adult DOB and shows it read-only; the age check is no longer possible to fail here.
- **Address auto-suggest:** V1. V0.5 is plain input.

---

## 5. Screen 7.3 — Identity

### 5.1 Layout

Uses form step shell. Content:

```
Step 2 of 4

Your identity

We use your BVN to confirm your bank
account. The ID photo lets our team
verify your identity when we review.

┌───────────────────────────────────┐
│ ▪ Bank Verification Number (BVN)  │
├───────────────────────────────────┤
│ 22212345678                       │  ← 11-digit numeric input
└───────────────────────────────────┘
Don't share your BVN with anyone else.
Atlas uses it to confirm your bank
account matches your identity, and
to check our self-exclusion register.

space.600

▪ Government-issued ID

  Any one of:
  ○ Your National Identification Number (NIN)
  ○ Driver's licence
  ○ International passport
  ○ NIN slip (if you don't have your NIN to hand)

┌───────────────────────────────────┐
│                                    │
│         📷                         │   ← ID upload area, radius.large,
│                                    │       surface.elevated, dashed border,
│      Tap to add photo              │       ~180pt tall
│                                    │
│    Take a photo or upload one      │
│                                    │
└───────────────────────────────────┘

The photo should be clear, in colour,
and show all four corners of the ID.

           [ Next ]
```

### 5.2 States

**Default:** BVN empty, ID upload empty.

**BVN valid:** 11 digits entered; field shows subtle `✓` in state.success.

**BVN invalid:** *"BVN is 11 digits."*

**BVN duplicated (already used for another Atlas account — self-exclusion enforcement, ADR-010):**
> This BVN is on our self-exclusion list. If this is you, please contact us.

Hard-stop with support link. This ties into ADR-010 and is a compliance-critical branch.

**ID upload — initial:** as drawn.

**ID upload — image selected:** upload area transforms into a preview of the uploaded image with a *"Replace"* link overlay and an inline *"Uploading…"* progress bar.

**ID upload — succeeded:** preview stays, upload bar disappears, subtle `✓ Uploaded` label.

**ID upload — failed:** upload area returns to initial state; banner *"Upload failed. Try again."*

**Loading (Next tapped):** *"Saving…"*, advances to 7.4.

### 5.3 Copy

| Element | Copy |
|---|---|
| Step headline | Your identity |
| Context | We use your BVN to confirm your bank account. The ID photo lets our team verify your identity when we review. |
| BVN label | Bank Verification Number (BVN) |
| BVN help | Don't share your BVN with anyone else. Atlas uses it to confirm your bank account matches your identity, and to check our self-exclusion register. |
| BVN error — length | BVN is 11 digits. |
| BVN error — self-excluded | This BVN is on our self-exclusion list. If this is you, please contact us. |
| ID header | Government-issued ID |
| ID sub | Any one of: |
| ID options | Your National Identification Number (NIN) · Driver's licence · International passport · NIN slip (if you don't have your NIN to hand) |
| Upload prompt | Tap to add photo |
| Upload sub | Take a photo or upload one |
| Upload guidance | The photo should be clear, in colour, and show all four corners of the ID. |
| Upload uploading | Uploading… |
| Upload uploaded | ✓ Uploaded |
| Upload failed | Upload failed. Try again. |
| Replace link | Replace |

**Copy commentary:**

- *"Don't share your BVN with anyone else."* — this line is a small but real trust move. She has been told her whole adult life not to share her BVN. Atlas acknowledges the norm and confirms Atlas is inside it, not outside it. **Amended 2026-07-08 per REVIEW-001 §5.2** — the original draft said *"we only use it to confirm your bank account"*, a technical understatement rather than a mis-statement: Atlas also uses BVN to key the self-exclusion registry (ADR-010). Under NDPA transparency + purpose-limitation principles the user must be told all purposes; the amended copy names both.
- The ID list **prioritises NIN** (verifiable via NIMC through the KYC vendor per ADR-007) and **excludes Voter's card**. **Amended 2026-07-08 per REVIEW-001 §5.3** — voter's card has no photo standardisation, no counterfeit-resistance features comparable to the other IDs, and vendor OCR performance is poor; not a standard KYC document in Nigerian financial-services practice. NIN slip retained as fallback for users who don't have their NIN memorised.
- The self-exclusion branch (ADR-010) is the single most compliance-critical branch on this screen. The copy is deliberately soft (*"If this is you, please contact us."*) — not accusatory. A self-excluded user reaching this point may be having a difficult moment; the copy should be respectful. See also §8.3 rejected-state variant 5.6.d which handles the self-exclusion match discovered at claim-submit time (rather than at BVN-blur time) with a mental-health helpline reference.

### 5.4 Accessibility

- BVN input: `inputMode: numeric`, `maxLength: 11`, `autocomplete="off"` (BVN is not standard autofill).
- Upload area: `role="button"` with label *"Add a photo of your government ID. Tap to take a photo or upload one."*
- Uploaded state: image has alt text *"Your uploaded ID document"*.
- Replace link: `aria-label="Replace uploaded ID photo"`.
- Contrast: dashed border on the upload area is `color.divider.strong` (`#C9C3B7`) — 3:1 on surface.elevated, passes UI-component contrast requirement.

### 5.5 Interaction

- **BVN validation:** length only in V0.5 (server call to confirm BVN against user identity is Adaeze/Amelia joint concern for V1; V0.5 admin manually validates).
- **ID upload:** on tap, action sheet with *"Take a photo"* / *"Choose from library"* / *"Cancel"*. Camera permissions requested if needed.
- **Uploaded image storage:** stored in the outbox — server-side, once uploaded it lives in the object store (S3-compatible in V0.5) with a signed URL; not exposed to client after upload.
- **Replace:** re-triggers the action sheet.
- **Self-exclusion detected server-side:** on Next tap, server checks BVN against self-exclusion registry (ADR-010); if match, return an error and this screen re-displays with the self-exclusion error copy. **This is the compliance enforcement moment** — the design is only the surface; the enforcement is ADR-010.

---

## 6. Screen 7.4 — Payout details

### 6.1 Layout

Uses form step shell. Content:

```
Step 3 of 4

Where should we send the money?

Your bank account must be in your
legal name. If it's a joint account,
you must be the primary holder.

┌───────────────────────────────────┐
│ ▪ Bank                            │
├───────────────────────────────────┤
│ [Guaranty Trust Bank        ▾]    │  ← dropdown of Nigerian banks
└───────────────────────────────────┘

┌───────────────────────────────────┐
│ ▪ Account number                  │
├───────────────────────────────────┤
│ 0123456789                        │  ← 10-digit numeric
└───────────────────────────────────┘

  ⋯ Confirming account...             ← after both fields filled,
                                          Paystack Resolve API call
                                          (V1) — V0.5 shows a stub state

┌───────────────────────────────────┐
│  ✓ Chinelo Okonkwo                │  ← if successful, name returned by
│                                    │      bank confirms match. Read-only.
│  This matches your claim. Ready to │
│  proceed.                          │
└───────────────────────────────────┘

           [ Next ]
```

### 6.2 States

**Default:** both fields empty, no confirmation.

**Fields filled, confirming:** loading spinner + *"Confirming account…"* (Paystack Resolve API call. In V0.5 this is a stub that returns "matches" for a specific seed account and "mismatch" for anything else — enough to demo both paths).

**Confirmation succeeded, name matches claim:** as drawn — green tick + confirmation card.

**Confirmation succeeded, name does NOT match claim:**
> The name on this account is Emeka Okoye. This doesn't match the name on your claim (Chinelo Okonkwo). Enter an account in your own name, or edit your name on Step 1.

Next stays disabled. **Compliance branch — cannot bypass.**

**Confirmation failed (Paystack error / network):** *"We couldn't confirm the account. Check the account number and try again."*

### 6.3 Copy

| Element | Copy |
|---|---|
| Step headline | Where should we send the money? |
| Context | Your bank account must be in your legal name. If it's a joint account, you must be the primary holder. |
| Bank label | Bank |
| Account label | Account number |
| Confirming spinner | Confirming account… |
| Match confirmation | ✓ {name} / This matches your claim. Ready to proceed. |
| Name mismatch | The name on this account is {returned name}. This doesn't match the name on your claim ({claim name}). Enter an account in your own name, or edit your name on Step 1. |
| Confirmation failed | We couldn't confirm the account. Check the account number and try again. |

**Copy commentary:**

- *"Where should we send the money?"* as the step headline reframes the friction as service: we're asking so we can send you money, not asking to make you prove yourself.
- The name-mismatch branch is drafted with the strong assumption that Atlas will NOT pay to an account that doesn't match the winner's legal name. Adaeze to confirm; this is a compliance decision, not a UX one.

### 6.4 Accessibility

- Bank dropdown: searchable, ARIA combobox pattern.
- Account number: `inputMode: numeric`, `maxLength: 10`.
- Confirmation state announced via `aria-live="polite"` (*"Account confirmed. Chinelo Okonkwo. This matches your claim."*).
- Mismatch state announced via `aria-live="assertive"` (this is a stop-condition; user must know).

### 6.5 Interaction

- **On both fields filled:** debounce 300ms, then fire Paystack Resolve API. In V0.5 this is stubbed but the shape is the same.
- **Match:** enables Next.
- **Mismatch:** disables Next, prompts correction.
- **Name-mismatch edit link:** *"edit your name on Step 1"* is an inline link; tapping returns to step 7.2 with the name field focused. Progress is preserved.

---

## 7. Screen 7.5 — Review + submit

### 7.1 Layout

```
┌─────────────────────────────────────────┐
│                                         │
│  ← Back                    Save + close │
│                                         │
├─────────────────────────────────────────┤
│  ●●●●   Step 4 of 4                     │
├─────────────────────────────────────────┤
│                                         │  space.600
│                                         │
│  Review your claim                      │  ← display.card
│                                         │
│  Check everything below. Once you       │  ← body.default secondary
│  submit, our team takes over.           │
│                                         │
│                                         │  space.800
│                                         │
│  ┌───────────────────────────────────┐ │  ← ReviewSection — each of the 3
│  │  ▪ YOUR DETAILS         Edit →     │ │      form steps summarised as a card,
│  │                                    │ │      each with an Edit link that
│  │  Chinelo Okonkwo                   │ │      returns to the corresponding step
│  │  12 March 1993                     │ │
│  │  +234 803 000 0000                 │ │
│  │  chinelo@example.com               │ │
│  │  15 Herbert Macaulay Way,          │ │
│  │  Yaba, Lagos                       │ │
│  └───────────────────────────────────┘ │
│                                         │  space.400
│  ┌───────────────────────────────────┐ │
│  │  ▪ YOUR IDENTITY        Edit →     │ │
│  │                                    │ │
│  │  BVN  222•••••678                  │ │  ← BVN redacted middle 5 digits
│  │                                    │ │
│  │  ID uploaded                       │ │
│  │  [thumbnail 60x40pt of ID image]   │ │
│  └───────────────────────────────────┘ │
│                                         │  space.400
│  ┌───────────────────────────────────┐ │
│  │  ▪ PAYOUT              Edit →      │ │
│  │                                    │ │
│  │  Guaranty Trust Bank               │ │
│  │  Account 0123456789                │ │
│  │  ✓ Confirmed as Chinelo Okonkwo    │ │
│  └───────────────────────────────────┘ │
│                                         │
│                                         │  space.800
│                                         │
│  ┌───────────────────────────────────┐ │  ← ConsentCard (required),
│  │  ✓  I confirm the details above    │ │      radius.large surface.elevated
│  │     are true, complete, and belong │ │      hairline border
│  │     to me.                         │ │      checkbox unchecked by default
│  │                                    │ │
│  │  Providing false information may   │ │
│  │  void my claim and can be reported │ │
│  │  to Nigerian authorities.          │ │
│  └───────────────────────────────────┘ │
│                                         │  space.300
│  ┌───────────────────────────────────┐ │  ← ConsentCard (required),
│  │  ✓  I agree Atlas may process my   │ │      identical treatment
│  │     personal data — including my   │ │
│  │     BVN and my ID document — to    │ │
│  │     verify my identity, confirm    │ │
│  │     my bank account, pay my prize, │ │
│  │     and meet Atlas's regulatory    │ │
│  │     obligations.                   │ │
│  │                                    │ │
│  │  Full details are in the Privacy   │ │
│  │  Notice. You can withdraw this     │ │
│  │  consent later, but it will pause  │ │
│  │  your claim.                       │ │
│  └───────────────────────────────────┘ │
│                                         │  space.300
│  ┌───────────────────────────────────┐ │  ← ConsentCard (optional),
│  │  ✓  You may publish my first name, │ │      same treatment. This one
│  │     last initial, and city on the  │ │      is NOT required for Submit;
│  │     Atlas winner announcement.     │ │      label is prefixed "Optional."
│  │                                    │ │
│  │  Optional. If you'd rather stay    │ │
│  │  anonymous, we'll publish          │ │
│  │  "Winner — {city}" instead.        │ │
│  └───────────────────────────────────┘ │
│                                         │
│                                         │  space.800
│                                         │
│  ┌───────────────────────────────────┐ │
│  │           Submit claim             │ │  ← primary button, disabled until
│  └───────────────────────────────────┘ │      BOTH required checkboxes ticked
│                                         │      (optional one has no effect on
│                                         │       enable state)
│                                         │
│                                         │  space.400
│                                         │
│  What happens next  →                   │  ← inline link centered, opens sheet
│                                         │      recap of the "what happens next"
│                                         │      list from 7.1
│                                         │
└─────────────────────────────────────────┘
```

### 7.2 Components used

- Form step shell (§3).
- `ReviewSection` — new; card with eyebrow + summary + Edit link.
- `ConsentCard` — new; checkbox + explanatory text in a card.
- `Button` (primary).
- `InlineLink` — "What happens next" (opens sheet).

### 7.3 States

**Default:** all sections filled from previous steps; both required checkboxes unchecked; optional publication-consent checkbox unchecked (default = anonymous); Submit disabled.

**Both required checkboxes ticked:** Submit enabled. Optional checkbox has no effect on enable state — it only sets the publication-consent flag on the submitted claim.

**Submit tapped (loading):** button label *"Submitting…"*; button non-interactive. Backend call fires (idempotent per ADR-004 with `claim_attempt_id`).

**Submit succeeded:** navigate to screen 7.6.

**Submit failed (network):** banner *"We couldn't submit your claim. Try again in a moment."*

**Submit failed (server validation — e.g. new self-exclusion match, duplicate claim on the ticket):** specific error banner + next-steps line.

### 7.4 Copy

| Element | Copy |
|---|---|
| Step headline | Review your claim |
| Context | Check everything below. Once you submit, our team takes over. |
| Section eyebrows | YOUR DETAILS / YOUR IDENTITY / PAYOUT |
| Edit link (per section) | Edit → |
| BVN display | 222•••••678 (first 3 + last 3 + redacted middle) |
| ID uploaded label | ID uploaded |
| Payout confirmation | ✓ Confirmed as {name} |
| Consent 1 label (required) | I confirm the details above are true, complete, and belong to me. |
| Consent 1 explanation | Providing false information may void my claim and can be reported to Nigerian authorities. |
| Consent 2 label (required) | I agree Atlas may process my personal data — including my BVN and my ID document — to verify my identity, confirm my bank account, pay my prize, and meet Atlas's regulatory obligations. |
| Consent 2 explanation | Full details are in the Privacy Notice. You can withdraw this consent later, but it will pause your claim. |
| Consent 3 label (optional) | You may publish my first name, last initial, and city on the Atlas winner announcement. |
| Consent 3 explanation | Optional. If you'd rather stay anonymous, we'll publish "Winner — {city}" instead. |
| CTA (default) | Submit claim |
| CTA (loading) | Submitting… |
| What-happens-next link | What happens next → |
| Error banner (network) | We couldn't submit your claim. Try again in a moment. |

### 7.5 Accessibility

- **Focus order:** Back → Save + close → Progress → Step headline + context → ReviewSection 1 (composite, Edit link individually focusable inside) → ReviewSection 2 → ReviewSection 3 → Consent 1 (required) → Consent 2 (required) → Consent 3 (optional, "Optional" prefix announced) → Submit → What-happens-next link.
- **Section reads:** composite readable summary; Edit link labelled *"Edit your details / your identity / your payout"*.
- **Consent checkboxes:** each has `aria-describedby` pointing at its own explanation paragraph, and Consent 3's `aria-label` is prefixed with the word "Optional" so screen-reader users hear the distinction without visual affordance.
- **Submit button state announcement:** button has `aria-describedby` that reads *"Submit is enabled once both required consents are ticked. The publication consent is optional."*
- **BVN redaction:** read as *"BVN, first three digits two two two, middle five hidden, last three six seven eight"*.

### 7.6 Interaction

- **Edit link (per section):** navigates to the corresponding form step (7.2, 7.3, 7.4). Progress dots update to show which step is now current. On Next from that step, user returns to 7.5.
- **What happens next:** opens a bottom sheet with the numbered list from 7.1 §2.4. Close returns to 7.5.
- **Submit:** fires backend `POST /claims` with `Idempotency-Key: claim_attempt_id`. On success → 7.6.

---

## 8. Screen 7.6 — Claim received

### 8.1 Layout

```
┌─────────────────────────────────────────┐
│                                         │
│                                         │  space.1600
│                                         │
│              ✓                          │  ← 64pt gold check-in-circle
│                                         │
│         Claim received.                 │  ← display.section, centered
│                                         │
│    We'll be in touch within             │  ← body.default, centered secondary
│    1 working day.                       │
│                                         │
│                                         │  space.1200
│                                         │
│  ─────────────────────────────          │  ← hairline
│                                         │
│  ▪ CLAIM REFERENCE                       │  ← label.micro gold uppercase, centered
│                                         │
│  CL-04829-6JQ7                          │  ← body.mono 20pt, centered
│                                         │      color.text.primary
│                                         │
│  ─────────────────────────────          │
│                                         │
│                                         │  space.800
│                                         │
│  Status                                 │  ← type.display.card
│                                         │
│  ┌───────────────────────────────────┐ │  ← StatusTimeline
│  │  ● Claim received                  │ │      radius.large surface.elevated
│  │     8 July, 20:14                  │ │      elevation.0
│  │                                    │ │
│  │  ○ Under review                    │ │
│  │     usually within 1 working day   │ │
│  │                                    │ │
│  │  ○ Approved                        │ │
│  │                                    │ │
│  │  ○ Payment sent                    │ │
│  │     to Guaranty Trust ••6789       │ │
│  │                                    │ │
│  │  ○ Complete                        │ │
│  │                                    │ │
│  └───────────────────────────────────┘ │
│                                         │
│                                         │  space.800
│                                         │
│  ┌───────────────────────────────────┐ │
│  │       Back to My tickets           │ │  ← button, secondary variant
│  └───────────────────────────────────┘ │
│                                         │
│                                         │  space.400
│                                         │
│  Save reference to notes                │  ← inline link, centered
│                                         │      copies claim ref to clipboard
│                                         │
└─────────────────────────────────────────┘
```

### 8.2 Components

- `SplashCheck` (reused — gold check + label pattern).
- `SectionLabel` (gold eyebrow).
- `SectionHeadline`.
- `StatusTimeline` — new; vertical list of states with leading filled/hollow dot, timestamp when reached, "expected" sub-line when pending.
- `Button` (secondary).
- `InlineLink` — "Save reference to notes" (copies claim ref to clipboard with toast).

### 8.3 States

**Just submitted (as drawn):** first status dot filled (Claim received) with timestamp; all others hollow with pending metadata where useful.

**Under review:** second dot filled.

**Approved (operator marked in admin):** third dot filled + timestamp. Adds a line: *"Approved by {operator} on {date}."*

**Payment sent:** fourth dot filled. Includes payment reference (mono).

**Complete:** all dots filled. Header check-in-circle changes to a *"You've been paid."* variant with copy: *"₦2,000,000 was sent to Guaranty Trust ••6789 on {date}."*

**Rejected (rare, hard case):** timeline shows a state.attention (amber) or state.danger (terracotta) indicator depending on scenario; specific message with next-steps. **Amended 2026-07-08 per REVIEW-001 §5.6** — Adaeze drafted four state variants below. The corresponding backend state on the claim state machine (per §10 Q15) is `rejected` with a `reason_code`; frontend switches copy per code.

**Variant 5.6.a — `kyc_failed` (identity did not match documents cleanly):**

Timeline second dot: *"Additional information needed"*, filled in `color.state.attention` (not danger — this is not an accusation).

> **We need to take another look.**
>
> The details you submitted didn't match cleanly against our identity checks. This can happen for a few reasons — a photo of an ID that wasn't clear, a name that appears differently on different documents, or details that don't line up with the bank account.
>
> Please **contact us at {support}** so we can help sort it out. Reference: **{claim_reference}**.

Primary CTA replaced by `Contact support` (mailto: in V0.5, WhatsApp in V1). Secondary link `Back to My tickets`.

**Variant 5.6.b — `bvn_mismatch` (BVN does not match the identity on the bank account):**

Timeline second dot: *"Bank account doesn't match"*, filled in `color.state.attention`.

> **Your BVN doesn't match the account you provided.**
>
> The name on your bank account (as returned by {bank_name}) is different from the name registered against your BVN. This usually means either the bank account isn't yours, or one of the records is out of date.
>
> **Update your bank details** if you provided the wrong account, or **contact your bank** if the name on your account needs correcting. Then come back and update this claim.
>
> Reference: **{claim_reference}**.

Primary CTA `Update bank details` (deep-links back to §6). Secondary link `Back to My tickets`.

**Variant 5.6.c — `under_review` (operator-set; suspected-fraud investigation without disclosure):**

Timeline second dot: *"On hold"*, filled in `color.state.attention`. Note: this state can be set by the operator without the user having done anything wrong; copy must not accuse.

> **Your claim is on hold pending review.**
>
> We've paused this claim while we look into some details. This can take a few working days. We'll email you as soon as we have an update.
>
> If you have information that would help, please **contact us at {support}** with your reference: **{claim_reference}**.

Primary CTA `Back to My tickets`. Secondary link `Contact support`.

**Variant 5.6.d — `self_excluded` (self-exclusion match detected at submit; ADR-010):**

Timeline second dot: *"Account closed"*, filled in `color.state.danger`. This is the most delicate variant — a user who self-excluded may not remember doing so, may be in a difficult moment, must be treated with care.

> **This account is on our self-exclusion register.**
>
> A member of our team will be in touch to explain what happens next and to arrange the refund of any wallet balance. If you'd like to talk to us before then, contact us at {support} or, if you'd prefer a professional, contact **{national gambling support helpline}**.
>
> Reference: **{claim_reference}**.

Primary CTA `Contact support`. Secondary link `Contact {national helpline}`. **Helpline identifier is TBD** — no mature GAMSTOP-equivalent exists in Nigeria (per ADR-010 alternatives-considered). Interim recommendation is a general mental-health line pending Adaeze research; this must land before real-user launch and is tracked as a Phase 3 gap in REVIEW-001 §5.6.d.

**Design pattern across all four variants:**

- The `SplashCheck` (gold check) header of the confirmation page is replaced by a state-appropriate glyph (`⚠` for attention, `⌀` for account-closed). The "Claim received" headline is replaced per variant.
- The `StatusTimeline` component is retained; only the second dot's state and label change.
- The claim reference (`{claim_reference}`) is always shown — even on rejection paths, the reference is how the user quotes the case to support.
- **No copy states the specific rule that fired** (which internal risk check flagged; which vendor returned what code). That detail lives in the operator surface (admin claim review UI, future wireframe).

### 8.4 Copy

| Element | Copy |
|---|---|
| Headline | Claim received. |
| Sub | We'll be in touch within 1 working day. |
| Claim ref label | CLAIM REFERENCE |
| Claim ref | CL-{ticket}-{4-char alphanumeric} |
| Status headline | Status |
| Timeline: received | Claim received |
| Timeline: review | Under review |
| Timeline: review pending sub (V0.5 demo only) | usually within 1 working day |
| Timeline: review pending sub (V1 real-user launch) | Most claims are reviewed within a few working days. |
| Timeline: approved | Approved |
| Timeline: payment | Payment sent |
| Timeline: payment sub (post-approval) | to {bank} ••{last 4} |
| Timeline: complete | Complete |
| Complete headline swap | You've been paid. |
| Complete sub | ₦{amount} was sent to {bank} ••{last 4} on {date}. |
| Secondary CTA | Back to My tickets |
| Save link | Save reference to notes |
| Save toast | Claim reference copied. |

**Copy commentary:**

- *"Claim received."* — three words. Understated, per the *"You're in."* pattern. Big check, small headline.
- Claim reference format `CL-04829-6JQ7` — 4-char suffix included so the reference is unique across the ticket number (which is not globally unique). Prefix `CL-` disambiguates from ticket numbers. The reference is the *thing she quotes if she needs to contact us* — it must be memorable and copy-friendly.
- Timeline "expected" text on pending steps is quiet and honest — *"usually within 1 working day"* rather than *"1 working day"* as if it were a hard SLA. **Note per REVIEW-001 §5.7:** this copy is approved for V0.5 investor demo scope only. Real-user launch must swap to the more conservative wording *"Most claims are reviewed within a few working days."* until Atlas has measured cadence across ≥30 real claims. Publishing a soft commitment on a cadence we haven't operated is avoidable exposure.
- *"You've been paid."* on complete state — echoes *"You're in."* and *"You won."*. The Atlas tone is *"declarative sentences about what just happened"*.

### 8.5 Accessibility

- Announcement on mount: *"Claim received. We'll be in touch within one working day. Claim reference C L, zero four eight two nine, six J Q seven."*
- Timeline: `role="list"` with each stage a `listitem`; completed items announced with a completion state; current pending item announced with expected timing.
- Save reference link: `aria-label="Copy claim reference to clipboard"`.
- Reduce motion: check appears solid; no scale-in.

### 8.6 Interaction

- **Back to My tickets:** navigates to wireframe 05 §2. The winning ticket now shows *"Claim in progress"* below the ticket number (updates via the ticket-detail primary CTA to *"See claim status"*).
- **Save reference to notes:** copies `CL-04829-6JQ7` to clipboard; toast per §8.4.
- **Status timeline updates:** V0.5 uses pull-to-refresh; V1 will support push updates.
- **Return to this screen:** accessible from the ticket detail winning variant CTA (*"See claim status"*) at any time.

---

## 9. Cross-flow notes

- **Idempotency (ADR-004):** every step of the form (7.2 save, 7.3 save, 7.4 save, 7.5 submit) is idempotent with a `claim_attempt_id` scoped to this ticket + user. Retries return the original result.
- **Audit log (ADR-005):** every state transition on the claim (created, personal-details-saved, identity-saved, payout-saved, submitted, under-review, approved, payment-sent, complete) writes to the hash-chained audit log.
- **Self-exclusion (ADR-010):** BVN check on 7.3 hits the self-exclusion registry. Match = hard-stop.
- **Ledger (ADR-003):** on payment-sent transition, a journal entry moves the funds from the prize pool account to a "paid out" account. Not visible on the consumer surface.
- **KYC vendor (ADR-007):** V0.5 uses `ManualApproveStub`; operator eyeballs the ID photo in admin and marks the claim approved. V1 swaps in a real vendor (Smile / Dojah / Prembly) — same claim flow surface, better backend validation.
- **Payment adapter (ADR-008):** V0.5 stubs the actual payout. V1 uses Paystack Transfer API (or bank direct). The consumer surface makes no assumption about which is in use.

---

## 10. Open questions for founder + agents

### For founder:

1. **Form step count — 4.** Could compress to 3 (merge identity + payout into "verification"). Recommend keep 4 — each step is a different *context* for the user (self-knowledge vs finding-your-BVN vs opening-your-banking-app). Compression saves screens at the cost of forcing context switches within a screen.
2. **"I'll come back later" link on the intro (§2.6)** — very deliberate. A winner shouldn't feel trapped in the claim flow. Any pushback?
3. **Claim reference format `CL-04829-6JQ7`** — the 4-char suffix ensures uniqueness across ticket numbers. If you prefer sequential (`CL-000001`, `CL-000002`), we lose the ticket-number embedding. Recommend keep — quoting your claim ref should reference *which ticket* it's for.
4. **Status timeline on 7.6 rather than a status page separate from the claim flow.** The claim-received screen IS the status page. On return, the user comes back to this screen (7.6). Confirm this is right (vs a separate "My claims" surface).
5. **No physical prize handling in V0.5.** All V0.5 seed prizes are cash. Confirm this is fine for the investor demo?

### For ⚖️ Adaeze — RESOLVED 2026-07-08 by REVIEW-001

6. **Age gate on DOB** — resolved §5.1: 18 is correct. **Also moved upstream to registration (wf-01 amendment 2026-07-08)** so under-18 users are blocked before entering draws, not just at claim time.
7. **BVN handling** — resolved §5.2: help copy amended to disclose the self-exclusion purpose (applied §5.3 above). Redacted display (`222•••••678`) approved as-is.
8. **ID types accepted** — resolved §5.3: Voter's card removed, NIN promoted to primary, NIN slip retained as fallback. Applied §5.3 above. **Amelia — confirm the KYC adapter (ADR-007) supports NIN verification via NIMC across the shortlisted vendors.**
9. **Bank account name-match hard-stop** — resolved §5.4: confirmed non-negotiable. AML posture + consumer protection + chargeback defensibility. Design already right; no change needed.
10. **Consent language on 7.5** — resolved §5.5: replaced with two-required + one-optional checkbox pattern. Applied §7.5 above.
11. **Rejected claim state copy** — resolved §5.6: four state variants (kyc_failed / bvn_mismatch / under_review / self_excluded) drafted by Adaeze. Applied §8.3 above.
12. **Timeline SLA copy** — resolved §5.7: current *"usually within 1 working day"* **rejected for real-user launch**; approved for V0.5 demo only. Real-launch swap to *"Most claims are reviewed within a few working days."* Applied to §8.4 above (both variants tabled).
13. **Winner-name publication consent** — resolved §4.3 + §5.5: added as the third (optional) consent checkbox on §7.5 above. **Non-winning-surface impact:** anonymous variant of the reveal page (*"Winner — {city}"*) is a V1 pre-launch design task; flagged in wf-06 amendment 2026-07-08.
14. **ID image storage + retention** — partially resolved §5.9: application-code posture is correct per ADR-007. Retention period, deletion-on-request workflow, S3 SSE-KMS encryption, S3 access logging, and retention triggers are all Phase 3 gaps. Adaeze + Tobi joint owner. Adaeze will land the retention *policy*; Tobi will land the infra; Sally will design the V1 Settings "Delete my data" flow when policy is confirmed.

Also flagged by Adaeze in REVIEW-001 §6 (not originally in Sally's question list):

- **R-FREE-01** — postal address for free entry does not exist as a leased P.O. box. Placeholder acceptable for demo; real address required for real-user launch.
- **R-SKILL-01** — V0.5 skill question has no rate-limit or lockout after N wrong answers; the "filter" is theatrical. 3-strike + cooldown is a real-launch Ticket-module invariant.
- **Self-exclusion wallet-refund flow** (ADR-010 §User-facing) not surfaced anywhere in the consumer flow. V1 Settings design task.
- **NDPA 2023 footings** absent across the board — data-subject rights UI, DPO contact, granular consent at registration, privacy notice draft. Phase 3 blockers.

### For 💻 Amelia:

15. **Claim state machine.** 6 states: `created → in_review → approved | rejected → payment_pending → paid | payment_failed → complete`. Confirm this matches the intended backend model, and whether `payment_failed` needs a distinct consumer-facing state (recommend it does — status 7.6 needs a variant).
16. **Server-side self-exclusion check on 7.3.** Hit the ADR-010 registry on `POST /claims/{id}/identity` — reject with a specific error code that the client maps to the self-exclusion copy on 7.3.
17. **Paystack Resolve API integration** for account-name match on 7.4 — V0.5 stubs this, V1 wires the real call. Confirm this fits into the payment adapter interface (ADR-008).
18. **Claim reference generation** — server-side, deterministic per claim, format `CL-{ticket_number}-{4char alphanumeric}` where the 4-char suffix is derived from the claim ID (not random — so on a retry we get the same ref, per ADR-004 idempotency).
19. **File upload for ID photo.** `multipart/form-data`, max 5MB, image types only, virus scan async (V1 concern — V0.5 skips).
20. **Long-form state persistence (Save + close).** Every step save is a `PATCH` on the claim resource; state survives across sessions and devices.

---

## 11. Cross-references

- Flow source: `v0.5-demo-plan.md §2` (step 7).
- Upstream entry points: `05-my-tickets.md §2.5 / §3.2` (winning-ticket CTA), `06-draw-completes-notification.md §2.6, §3.6` (reveal CTA).
- Post-submit destination: this screen (7.6) is also the status page — accessible from the winning-ticket CTA.
- Tokens: `tokens.md`.
- Tone: `tone-doc.md` §1 (Bentley delivery posture), §5 (copy voice, declarative sentences).
- ADRs: ADR-003 ledger, ADR-004 idempotency, ADR-005 audit log, ADR-007 KYC vendor, ADR-008 payment adapter, ADR-010 self-exclusion.
- Operator side (future wireframe): admin claim review + approve UI, part of Week 2 admin flows.

---

🎨 *End of wireframe 07, and end of Day 6.*

*Day 6 complete. Wireframes 06 (draw completes / notifications) and 07 (winner claim start) delivered. This closes the primary consumer flagship flow up to and including winner initiation.*

*Progress: 7 wireframes done in 6 days. Consumer surface is essentially drafted end-to-end. Week 1 has one day left (Day 7 — buffer + copy-block refinement + week-1 checkpoint per tone-doc.md §8) before we cross into Week 2 (operator flows + trust story + wow moment).*

*Two big review asks before Day 7:*

*1. Adaeze needs to weigh in on the compliance-load-bearing surfaces — wireframe 03 (free-entry disclosure), 04 (skill question mechanic), 06 (winner name publication), 07 (KYC + BVN + consent — the biggest ask). This is best done as a single Adaeze pass, not piecemeal.*

*2. Founder review of the consumer flow end-to-end. Six days of design, six wireframes, one tone doc, one token doc. Read as a set, not as individual files, because the ritual anchors ("You're in", "Not this time", "prize competition, not a lottery", the ticket artefact language, the hash typography motif) are load-bearing across screens.*

*Say the word and I'll continue into Day 7 refinements, or hold for review.*

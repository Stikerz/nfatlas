# Wireframe 10 — Transcribe Free Entry

**Drafted:** 2026-07-08 (Day 9 per `tone-doc.md §8`)
**Drafted by:** 🎨 Sally (BMad UX Designer)
**Status:** Draft — **routed to ⚖️ Adaeze mid-draft per REVIEW-001 §7** for the parity invariant review (transcription flow must produce ticket rows structurally identical to paid-route rows). Founder review pending Week 2 exit.
**Covers:** Flagship flow step 10 from `v0.5-demo-plan.md §2` — *"Transcribe free entry — form: enter user identifier + entry slip reference → creates a free-route ticket in the same pool."*
**Surface:** Next.js admin, inside the shell established in wireframe 08 §1.
**Pairs with:** `03-free-entry-disclosure.md` (the consumer promise this flow honours), `09-create-draw.md`, `tokens.md`, ADR-003 (ledger — free-route tickets carry no monetary movement but still write journal rows for symmetry per Adaeze), ADR-004 (idempotency on ticket creation), ADR-010 (self-exclusion check runs on transcribed entries too).

---

## 0. The one thing this screen has to do right

Sally's promise on wireframe 03 §3.4: *"We transcribe every valid entry into the same pool. Same odds. Same pool. Same shot."*

Adaeze's response in REVIEW-001 §2.2: *"Every valid free-route entry is transcribed into the same table row-space as paid entries. No separate table, no 'free-route' pool that is silently smaller. The transcription flow ... must produce a `ticket` row indistinguishable from a paid-route `ticket` row except for the `entry_source` field."*

**This wireframe is where that promise stops being a promise and starts being a system.** Every design decision below serves that invariant.

If the operator can, through this UI, produce a ticket that behaves differently from a paid-route ticket (different table, different indexing, different odds), the promise is broken. If the operator can, through this UI, drop or lose a valid slip without a visible audit trail, the promise is broken. If the operator can, through this UI, backdate a free-route entry so it appears to have arrived before sale close, the promise is broken.

Everything below is either honouring one of those invariants, or is genuinely optional.

**Non-goals for V0.5:**
- OCR of scanned entry slips. V1.
- Bulk CSV import. V1 (though the interaction pattern in §3 supports it structurally).
- Postal-address integration with courier or PO-box provider APIs. Operator manually collects mail; V1.
- Physical slip storage / archiving workflow. Operational (not UX); noted for real-launch runbook.

---

## 1. Where in the shell

Sidebar → **OPERATE → Free entries** → the transcription surface for the currently active draw.

If no draw is currently in its sales window, the surface shows an empty state (*"No draw is open for entries right now. The next draw opens {when}."*). Free-route slips received outside a sales window are transcribed against the next sales window when it opens (operational policy — Adaeze to confirm this is what the promise means).

---

## 2. Screen 10.1 — Transcribe surface

### 2.1 Layout (inside admin shell)

```
< inside admin shell >

  Free entries — transcribe

  This draw's free route has received 87 entries so far.       ← body.default, secondary
  Sales close 12 Jul 2026, 20:00 WAT. All slips postmarked
  before that time are eligible.

  space.800

  ┌──────────────────────────────────────────────────────────┐
  │  ▪ ACTIVE DRAW                                            │  ← summary strip, gold eyebrow
  │                                                          │
  │  ₦2,000,000 in cash draw                                 │
  │  Sales open · Closes 12 Jul 2026, 20:00 WAT              │
  │  1,160 paid entries · 87 free-route entries              │  ← body.small, entry counts
  │  Total pool: 1,247                                        │      always visible
  └──────────────────────────────────────────────────────────┘

  space.600

  ┌──────────────────────────────────────────────────────────┐
  │  ▪ NEW SLIP                                               │
  │                                                          │
  │  ┌────────────────────────────────────────────────────┐ │
  │  │ ▪ Postal slip reference                            │ │
  │  ├────────────────────────────────────────────────────┤ │
  │  │ FE-04829                                           │ │  ← text input, required
  │  └────────────────────────────────────────────────────┘ │      unique per-draw
  │  The reference is stamped on the slip when it's           │  ← body.small helper
  │  received at the P.O. box. Format: FE-{5-digit}.          │
  │                                                          │
  │  ┌────────────────────────────────────────────────────┐ │
  │  │ ▪ Postmark date                                    │ │
  │  ├────────────────────────────────────────────────────┤ │
  │  │ 10 Jul 2026                                        │ │  ← date picker
  │  └────────────────────────────────────────────────────┘ │      must be ≤ sales close
  │  On the envelope. Used to validate the slip was mailed   │
  │  before sales closed.                                     │
  │                                                          │
  │  space.400                                                │
  │                                                          │
  │  ▪ Entrant identity                                       │  ← group sub-header
  │                                                          │      body.default primary
  │                                                          │
  │  Enter any one of the following. We match to an          │  ← body.small secondary
  │  existing Atlas account. If no account matches, the       │
  │  slip is queued for review (see §4).                     │
  │                                                          │
  │  ┌────────────────────────────────────────────────────┐ │
  │  │ Match by                                           │ │
  │  ├────────────────────────────────────────────────────┤ │
  │  │ [ Email                                        ▾ ] │ │  ← dropdown: Email / Phone / BVN
  │  └────────────────────────────────────────────────────┘ │
  │                                                          │
  │  ┌────────────────────────────────────────────────────┐ │
  │  │ Email                                              │ │
  │  ├────────────────────────────────────────────────────┤ │
  │  │ chinelo@example.com                                │ │  ← input; type changes with
  │  └────────────────────────────────────────────────────┘ │      dropdown selection
  │                                                          │
  │  ⋯ Matching…                                              │  ← inline status
  │                                                          │      (after both fields set)
  │  ┌────────────────────────────────────────────────────┐ │
  │  │  ✓ Matched                                         │ │  ← Match result, radius.large
  │  │                                                    │ │      surface.subtle
  │  │  Chinelo Okonkwo                                   │ │      hairline border
  │  │  Registered 3 Jul 2026 · +234 803 000 0000        │ │      solid state.success 4pt
  │  │  Not self-excluded                                 │ │      left border
  │  └────────────────────────────────────────────────────┘ │
  │                                                          │
  │  space.400                                                │
  │                                                          │
  │  ▪ Skill answer on slip                                   │
  │                                                          │
  │  Question that appeared with this slip's issue date:     │  ← body.default primary
  │  Which of these is the capital of Nigeria?               │  ← body.default primary
  │                                                          │
  │  ┌────────────────────────────────────────────────────┐ │
  │  │ Answer written on slip                             │ │
  │  ├────────────────────────────────────────────────────┤ │
  │  │ [ Abuja                                        ▾ ] │ │  ← dropdown of 4 options
  │  └────────────────────────────────────────────────────┘ │      matching the question
  │                                                          │      correct answer highlighted
  │                                                          │      only after transcription
  │                                                          │
  │  ⓘ Correct answer will be shown on submit.                │  ← body.small secondary
  │     Wrong answers void the slip.                          │
  └──────────────────────────────────────────────────────────┘

  space.800

  [ Cancel ]              [ Save + transcribe next  ]  [  Save + close  ]
                          ← secondary                     ← primary
                             saves this slip,             saves this slip,
                             returns to fresh form        returns to §4 index
```

### 2.2 Components used

- `AdminPageHeader` (headline + context sentence).
- `SummaryStrip` — the ACTIVE DRAW summary card at the top; new but simple. Composition: eyebrow + draw title + status line + entry-counts line. **The entry counts are always visible** on this surface — the operator sees the pool composition growing as they work.
- `FormGroupCard` — reused from wf-09.
- `TextInput` / `DateInput` / `Dropdown` — form primitives.
- `MatchStatusRow` — new; small inline status that goes through `[empty] → [matching…] → [matched | no match]` states. On match, expands to the `MatchResultCard`.
- `MatchResultCard` — new; a card with the matched account's name, registration date, contact, and **self-exclusion status**. The self-exclusion status is the reason this card exists as a card — the operator must see the ADR-010 check pass (or fail) before they transcribe.
- `Button` (primary, secondary).
- `InlineLink` (Cancel).

### 2.3 States

**Default:** empty form. All required-field indicators visible.

**Slip reference validating:** on blur, the reference is checked for uniqueness within this draw. If duplicate: *"This reference was already transcribed on {date}. Was it accidentally posted twice? Contact founder before saving."*

**Postmark date validating:** on blur, must be ≤ sales close date. If after: *"This slip was postmarked after sales closed on 12 Jul 2026, 20:00 WAT. It is not eligible for this draw. Queue for next draw instead."* — with a *"Queue for next draw →"* inline action link.

**Matching entrant identity:**
- Both `match by` type and value present → fires match request.
- `⋯ Matching…` inline label with a soft spinner.
- **Matched, not self-excluded:** MatchResultCard success variant (green tick, name, meta, "Not self-excluded" line).
- **Matched, self-excluded:** MatchResultCard danger variant. Full block. Copy: *"This account is on the self-exclusion register. Do not transcribe this slip. Log the slip in the self-exclusion incident log per compliance runbook."* Save button disabled.
- **No match found:** MatchResultCard attention variant (amber). Copy: *"No Atlas account matches. This slip is queued for review — a real person may have entered without registering, or the slip's details need clarification. See queue at §4."* Save button changes to `Queue this slip`.
- **Match failed (system error):** *"We couldn't check this identity. Try again in a moment."* Save button disabled.

**Skill answer:** dropdown always shows all 4 options. Correct answer is not highlighted in the dropdown (would leak). On submit, if the answer is wrong, the slip is transcribed as "void — wrong skill answer" and logged; §4 shows voided-slip counters.

**Save + transcribe next (loading):** button label *"Saving…"* + spinner. On success, form resets to empty (except the ACTIVE DRAW strip's entry counts increment) and focus returns to the slip reference field.

**Save + close (loading):** same but navigates back to §4 index on success.

**Idempotency:** every save carries `Idempotency-Key: FE-{ref}-{draw_id}`. Duplicate submits during network stutter return the original result.

### 2.4 Copy

| Element | Copy |
|---|---|
| Page headline | Free entries — transcribe |
| Context | This draw's free route has received {n} entries so far. Sales close {close_time}. All slips postmarked before that time are eligible. |
| Summary eyebrow | ACTIVE DRAW |
| Summary title | {prize} draw |
| Summary status | Sales open · Closes {close_time} |
| Summary counts | {paid} paid entries · {free} free-route entries |
| Summary total | Total pool: {total} |
| Form eyebrow | NEW SLIP |
| Slip ref label | Postal slip reference |
| Slip ref helper | The reference is stamped on the slip when it's received at the P.O. box. Format: FE-{5-digit}. |
| Slip ref error — duplicate | This reference was already transcribed on {date}. Was it accidentally posted twice? Contact founder before saving. |
| Postmark label | Postmark date |
| Postmark helper | On the envelope. Used to validate the slip was mailed before sales closed. |
| Postmark error — late | This slip was postmarked after sales closed on {close_time}. It is not eligible for this draw. |
| Late-slip inline action | Queue for next draw → |
| Identity group header | Entrant identity |
| Identity group helper | Enter any one of the following. We match to an existing Atlas account. If no account matches, the slip is queued for review (see queue). |
| Match-by label | Match by |
| Match-by options | Email / Phone / BVN |
| Match status — searching | ⋯ Matching… |
| Match success — heading | ✓ Matched |
| Match success — meta line | Registered {date} · {phone_e164} |
| Match success — exclusion state | Not self-excluded |
| Match self-excluded — heading | ⌀ Account is self-excluded |
| Match self-excluded — body | This account is on the self-exclusion register. Do not transcribe this slip. Log the slip in the self-exclusion incident log per compliance runbook. |
| Match not-found — heading | ⚠ No matching account |
| Match not-found — body | No Atlas account matches. This slip is queued for review — a real person may have entered without registering, or the slip's details need clarification. See queue. |
| Match error | We couldn't check this identity. Try again in a moment. |
| Skill group header | Skill answer on slip |
| Skill question label | Question that appeared with this slip's issue date: |
| Skill answer label | Answer written on slip |
| Skill helper | Correct answer will be shown on submit. Wrong answers void the slip. |
| Cancel | Cancel |
| Save + next CTA | Save + transcribe next |
| Save + close CTA | Save + close |
| Save success toast | Slip {ref} transcribed. |
| Slip voided toast | Slip {ref} recorded as void — wrong skill answer. |

**Copy commentary:**

- *"Slip {ref} transcribed"* rather than *"Ticket issued"* — the operator's mental model here is *slips*, not tickets. The ticket is a downstream artefact of the slip transcription. Naming the operator's action after their mental model reduces error.
- The self-exclusion match copy is deliberately operational (*"Log the slip in the self-exclusion incident log per compliance runbook"*) rather than consumer-facing — the operator needs to know what to do next, not just what happened.
- *"Was it accidentally posted twice?"* on the duplicate-reference error — a small trust move for the entrant. Duplicates happen; the copy assumes benign explanation first.

### 2.5 Accessibility

- **Focus order:** headline → slip ref → postmark → match-by dropdown → identity value → (match card announces when it lands) → skill answer dropdown → Cancel → Save+next → Save+close.
- **Match card state changes:** announced via `aria-live="assertive"` — this is the critical operational moment (self-exclusion match is the highest-stakes state).
- **Self-excluded state:** the card is `role="alert"` — highest AT priority.
- **Skill answer dropdown:** `aria-label="Answer as written on the slip. Do not correct the entrant's answer."`
- **Save buttons:** disabled when the match state is self-excluded or when required fields are incomplete; `aria-disabled` with a helper span announced on focus attempt.

### 2.6 Interaction

- **Debounced match request:** identity dropdown + value field triggers a lookup 500ms after the last keystroke (or immediately on paste). Cancels prior requests.
- **Save + transcribe next:** the fast path. Operator processes 10 slips in a row without leaving the form. Focus returns to slip-reference field. The `ACTIVE DRAW` strip's entry counts update in place; the operator sees the free-route count climb as they work — small feedback loop that makes the invariant tangible.
- **Enter behaviour:** Enter on the last field of a form submits with Save+next (the batch mode is the common case). Shift+Enter forces Save+close.
- **What happens server-side (documented so the design contracts hold):** the server issues a ticket via the same code path used by paid entries. The ticket carries `entry_source = "free_route"`, `postmark_date`, `postal_ref`, and a link to the transcribed-by operator + timestamp. **No separate table. No shortcut. The `tickets` row is structurally identical to a paid-route row.** This is the Adaeze parity invariant honoured in code.
- **Ledger side effect:** per Adaeze's note (informal, to be confirmed), even though no money moves for a free-route ticket, a `ticket_issued` journal event is written (with zero amount) so the audit trail treats both routes with the same shape. Amelia to confirm this is right or overkill.

---

## 3. Screen 10.2 — Slip queue (unmatched / voided / late)

Not all slips are transcribable in one pass. This subscreen holds the ones that need manual attention.

### 3.1 Layout

```
< inside admin shell >

  Free entries — queue

  Slips that need review before they can be transcribed        ← body.default, secondary
  into the pool, or that have been voided.

  space.800

  ┌───┬──────────┬─────────┬──────────────┬────────────┬─────┐
  │ # │ Ref      │ Postmark│ Reason       │ Received   │ Act │
  ├───┼──────────┼─────────┼──────────────┼────────────┼─────┤
  │ 1 │ FE-04901 │ 10 Jul  │ No match     │ 12 Jul     │ [→] │
  │ 2 │ FE-04902 │ 11 Jul  │ No match     │ 12 Jul     │ [→] │
  │ 3 │ FE-04903 │ 13 Jul  │ Postmark late│ 13 Jul     │ [→] │
  │ 4 │ FE-04812 │ 08 Jul  │ Wrong answer │ 09 Jul     │ [○] │
  └───┴──────────┴─────────┴──────────────┴────────────┴─────┘

  4 slips in queue · 2 needing action · 2 informational

  [ + Add slip to queue ]  ← for slips received without going through 10.1
```

### 3.2 Behaviour

Rows tagged `No match` open a re-match flow (a lookup screen with a broader search). Rows tagged `Postmark late` offer "Queue for next draw" as the primary action (the slip is not for this draw but is still valid for the next one). Rows tagged `Wrong answer` are informational — the slip is void and stays in the queue as evidence.

### 3.3 Cross-reference

Full spec of the re-match subscreen is deferred to a follow-on wireframe (not in Day 9 scope). The invariant carried through: no re-match action creates a paid-route ticket. The re-match either produces a free-route ticket (structurally identical) or moves the slip to a queue for further review.

---

## 4. Design invariants for this flow

Recording explicitly because these are the operational realisations of the promises made in wireframe 03:

1. **Same table, same code path.** Every save on this surface calls the same `POST /admin/tickets` endpoint the paid-route flow calls, with `entry_source = "free_route"` as a field, not as a table selector.
2. **Self-exclusion check runs before ticket creation.** ADR-010 enforcement is not skipped for the free route. The match card surfaces the check result before the operator can save.
3. **Late slips are never backdated.** Postmark date is validated; late slips are visibly queued, not silently rejected or silently accepted with a fudged timestamp.
4. **Voided slips are recorded, not deleted.** Wrong skill answers void the slip but the void event is a persistent record. Regulator or auditor can see the void count.
5. **Every transcribed ticket carries operator + timestamp attribution.** The audit-log event for the ticket issuance includes `transcribed_by = {operator_id}` and `transcribed_at = {ts}`. This is a operator-accountability commitment.
6. **The entry-count strip is always visible.** The operator sees the free-route count grow as they work; the pool composition is not abstract.
7. **No bulk delete on transcribed tickets.** Once transcribed, a ticket can be cancelled (individually, with a cancellation event) but the row itself is not deletable. This preserves auditability.

---

## 5. Open questions for founder + Adaeze

### For founder:

1. **Save + transcribe next as default primary action.** Optimised for the batch case (operator processing 10 slips). If the more common case turns out to be one-off transcription, we swap primary to Save + close. Watch the demo behaviour before deciding.
2. **Reject vs void.** A wrong-answer slip is *voided* (recorded but excluded from the pool). Alternative: *rejected* (removed from record). Recommend void — the record matters for the auditor and for reconciling slip counts.
3. **Operator credential attribution on the ticket.** Every free-route ticket permanently records which operator transcribed it. Is this attribution visible to the entrant (probably not — feels invasive) or only to Atlas + auditor? Recommend Atlas-internal only.

### For ⚖️ Adaeze (early review requested per REVIEW-001 §7):

4. **The parity invariant (§0, §4.1).** Does this surface satisfy the invariant *"free-route tickets are structurally identical to paid-route tickets except for `entry_source`"*?
5. **Self-exclusion enforcement at transcription (§2.3).** Is the self-excluded state handled correctly on this surface? Should there be additional documentation (e.g. a note that the operator must destroy the physical slip after logging)?
6. **Postmark validation (§4.3).** Is the enforcement that postmark ≤ sales close correct? Any edge cases for postmarks that are missing or unreadable on the envelope?
7. **Ledger side effect for zero-amount ticket issuance (§2.6).** Adaeze — do you require a journal event even for free-route (no money), for symmetry with paid-route? Amelia will build to your ruling.
8. **Voided slip retention (§4.4).** Voided slips are kept as records; is there a retention period Atlas should commit to? Currently indefinite.
9. **Late slips (§2.3).** Slips postmarked after sales close are ineligible for this draw but queuable for the next. Confirm: is that policy defensible, or should late slips be flat-out returned to sender with no draw eligibility?
10. **Operator identity in audit trail (§4.5).** Every transcription writes `transcribed_by`. Is that sufficient, or do we need additional operator authentication step for each transcription (e.g. a second-factor prompt per slip)?

### For 💻 Amelia:

11. **`POST /admin/tickets` shared endpoint.** Both paid and free-route ticket creation go through the same endpoint, with `entry_source` as a request parameter. Confirm this fits the Ticket module boundary.
12. **Match lookup performance.** The identity lookup (email/phone/BVN → user) must handle a few thousand records at V0.5 scale, more at V1. Debounced 500ms; index on `users.email`, `users.phone_e164`, `users.bvn_hash`. Confirm.
13. **Idempotency key format `FE-{ref}-{draw_id}`.** Ensures the same slip-and-draw pair produces one and only one ticket even across retries. Confirm this fits the ADR-004 pattern.

---

## 6. Cross-references

- Flow source: `v0.5-demo-plan.md §2` (step 10).
- Consumer promise: `03-free-entry-disclosure.md §3` (the sheet that promises the transcription).
- Admin shell: `08-admin-login.md §1`.
- Related admin: `09-create-draw.md` (upstream — the draw whose free-route pool this fills), `11-close-and-reveal-draw.md` (downstream — transcription closes when sales close).
- Compliance review: `docs/compliance/reviews/REVIEW-001-v0.5-consumer-wireframes.md` §2.2 (parity invariant).
- ADRs: ADR-003 (ledger — journal event for symmetry), ADR-004 (idempotency), ADR-010 (self-exclusion enforcement at transcription).
- Tokens: `tokens.md`.
- Tone: `tone-doc.md` (admin voice, Nigerian operator name).

---

🎨 *End of wireframe 10. **Adaeze — this is the working draft you asked for.** Not polished; ready for parity-invariant + self-exclusion + operator-attribution review. Flag anything that would break the promise before I move to wf-11.*

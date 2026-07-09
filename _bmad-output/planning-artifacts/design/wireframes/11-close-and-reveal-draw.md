# Wireframe 11 — Close Draw (and cross-reference to Reveal in wf-12)

**Drafted:** 2026-07-08 (Day 9 per `tone-doc.md §8`)
**Drafted by:** 🎨 Sally (BMad UX Designer)
**Status:** Draft — pending founder review + ⚖️ Adaeze compliance review at end of Week 2. The close action is one of three cryptographic-artefact-producing operator actions (create, close, reveal); the design pattern is intentionally the same as wf-09 §5-6 (review → type-to-confirm → receipt).
**Covers:** Flagship flow step 11 from `v0.5-demo-plan.md §2` — *"Close draw — button. Sales stop. tickets_hash computed and displayed."*
**Surface:** Next.js admin, inside the shell (wf-08 §1).
**Pairs with:** `09-create-draw.md` (the commit whose corresponding close-artefact lives here), `12-reveal-draw.md` (Day 9 sibling — the third and final commit-reveal artefact), `tokens.md`, ADR-006 (protocol stage 3 — Close).

---

## 0. Why close needs its own screen

Close is a small action with a large consequence. When the operator taps close:

- Sales endpoint stops accepting tickets. (Consumer surface disables Enter button; wf-02 §3.3 closed state.)
- `tickets_hash = SHA-256(JCS-canonical(ticket_id_list))` is computed and written to the audit log (`draw.entries_snapshot` event per ADR-006 §Protocol stage 3).
- The pool of tickets is now **fixed**. Any post-close ticket creation would be a break of the commitment.

The visible artefact of close is `tickets_hash` — a second hash that joins the commitment hash from wf-09 in the trust story. Together they say: *"here is what Atlas committed to, and here is the exact set of tickets that were in the pool when sales ended."*

**Non-goals for V0.5:**
- Automatic close at scheduled time. V0.5 requires manual operator close (per plan §2 step 11 wording *"button"*). V1 adds a scheduler that auto-closes and notifies the operator.
- Close-with-refund workflow (for cancelled draws pre-reveal). V1 concern.
- Partial close (some ticket categories continue). Not in scope; draws are single-pool.

---

## 1. Where in the shell

Sidebar → **OPERATE → Draws → {active draw}** → the draw detail page → *Close draw* action.

The admin draw-detail page is not fully specced here (it's implicit context — a page showing the draw's parameters, live entry counts, transcribe-queue depth, and lifecycle actions). This wireframe covers the *close* action specifically, from the moment the operator taps *Close draw* on the detail page through to the close receipt.

---

## 2. Screen 11.1 — Pre-close review

### 2.1 Layout

```
< inside admin shell >

  ← Back to draw

  Close draw

  You're about to close sales on the ₦2,000,000 in cash draw.  ← body.default primary
  Once closed, no more tickets can enter the pool. The tickets
  hash is computed and published to the audit log.

  space.800

  ┌──────────────────────────────────────────────────────────┐
  │  ▪ POOL AT THIS MOMENT                                    │  ← summary card
  │                                                          │
  │  1,247 tickets                                            │  ← type.display.card
  │                                                          │
  │  1,160  Paid                                              │  ← two-column stat rows
  │     87  Free-route                                        │      body.default
  │  ────────────────────────                                 │
  │  1,247  Total                                             │
  │                                                          │
  │  ─────────────────────────────                            │
  │                                                          │
  │  Sales opened     08 Jul 2026, 14:00:00 WAT               │
  │  Sales close      12 Jul 2026, 20:00:00 WAT               │  ← the scheduled close
  │  Closing at       12 Jul 2026, 19:58:14 WAT               │  ← now-ish (early close                                                            │      allowed within a small
  │                                                          │      window; late close creates
  │                                                          │      a visible audit event)
  │                                                          │
  │  ─────────────────────────────                            │
  │                                                          │
  │  Free-entry queue    3 slips pending                      │  ← ChipRow with attention state
  │                                                          │
  │  ⚠ Three postal slips are still in the transcription       │  ← WarningNote
  │    queue. Close will exclude them from this pool.          │      color.state.attention
  │    Confirm they are void or transcribe them first.         │
  │                                                          │
  │  [ Go to queue ] [ Ignore and continue ]                  │  ← two inline actions
  └──────────────────────────────────────────────────────────┘

  space.600

  ┌──────────────────────────────────────────────────────────┐
  │  ▪ AFTER CLOSE                                            │
  │                                                          │
  │  When you close:                                          │
  │                                                          │
  │  1. Sales endpoint stops accepting new tickets            │  ← numbered list
  │     immediately. Consumer draw page enters closed state.  │
  │                                                          │
  │  2. Ticket list is canonicalized and hashed:              │
  │     tickets_hash = SHA-256(JCS-canonical(ticket_ids))     │  ← body.mono inline
  │                                                          │
  │  3. tickets_hash is written to the draw record and to     │
  │     the audit log (event `draw.entries_snapshot`).        │
  │                                                          │
  │  4. tickets_hash appears on the public draw page and      │
  │     is included in the public /proof endpoint.            │
  │                                                          │
  │  5. Draw enters "awaiting reveal" state. Reveal fires     │
  │     manually via wf-12 at or after 13 Jul 2026, 21:00     │
  │     WAT.                                                   │
  │                                                          │
  │  Close cannot be undone. Late transcriptions after close  │  ← body.default primary
  │  can only be admitted with a documented audit-log         │
  │  amendment — that path is intentionally awkward.          │
  └──────────────────────────────────────────────────────────┘

  space.1200

  [ Cancel ]                                    [  Close draw  ]
                                                   ↑ primary button
                                                     attention-tinted background
                                                     hint (per wf-09 §5.4)

  ⓘ Close is guarded by a confirmation modal.
```

### 2.2 Components used

- `AdminPageHeader` (headline + context).
- `PoolSummaryCard` — new; the "POOL AT THIS MOMENT" card. Composition: total-count display, paid/free rows, timing definition list, transcription-queue status. **The transcription-queue chip is the single most operationally important element on this screen** — it's what prevents an operator from closing while free-route slips are pending.
- `WarningNote` — reused from wf-09 §4.2; here surfaces the pending-queue condition.
- `AfterCloseExplainer` — reused pattern from wf-09 §5.4; a numbered list of what close does.
- `Button` (primary + secondary).
- `InlineLink`.

### 2.3 States

**Default (queue empty):** the WarningNote is absent. Close button is fully enabled and reads as a straightforward primary action.

**Default (queue has pending slips):** WarningNote visible as drawn; Close button remains enabled (the operator can proceed with the pending slips visible on record), but the two inline actions `[ Go to queue ] [ Ignore and continue ]` guide the operator to resolve the queue first.

**Close tapped:** opens modal 11.2.

**Cancel:** returns to the draw detail page.

### 2.4 Copy

| Element | Copy |
|---|---|
| Back link | ← Back to draw |
| Headline | Close draw |
| Context | You're about to close sales on the {prize} draw. Once closed, no more tickets can enter the pool. The tickets hash is computed and published to the audit log. |
| Pool eyebrow | POOL AT THIS MOMENT |
| Pool count | {total} tickets |
| Pool stat — paid | {paid} · Paid |
| Pool stat — free | {free} · Free-route |
| Pool stat — total | {total} · Total |
| Sales-opened row | Sales opened / {open_time} |
| Scheduled-close row | Sales close / {scheduled_close} |
| Closing-at row | Closing at / {now_ish} |
| Queue chip | Free-entry queue / {n} slips pending |
| Queue warning | {n} postal slips are still in the transcription queue. Close will exclude them from this pool. Confirm they are void or transcribe them first. |
| Queue action 1 | Go to queue |
| Queue action 2 | Ignore and continue |
| After-close eyebrow | AFTER CLOSE |
| After-close step 1 | Sales endpoint stops accepting new tickets immediately. Consumer draw page enters closed state. |
| After-close step 2 | Ticket list is canonicalized and hashed: `tickets_hash = SHA-256(JCS-canonical(ticket_ids))` |
| After-close step 3 | tickets_hash is written to the draw record and to the audit log (event `draw.entries_snapshot`). |
| After-close step 4 | tickets_hash appears on the public draw page and is included in the public /proof endpoint. |
| After-close step 5 | Draw enters "awaiting reveal" state. Reveal fires manually via the reveal screen at or after {reveal_time}. |
| Undo caveat | Close cannot be undone. Late transcriptions after close can only be admitted with a documented audit-log amendment — that path is intentionally awkward. |
| Cancel CTA | Cancel |
| Close CTA | Close draw |
| Close note | Close is guarded by a confirmation modal. |

**Copy commentary:**

- The *"intentionally awkward"* phrasing on the undo caveat is deliberate. Operators need to know that post-close amendment is possible (regulatory reality — mistakes happen and must be correctable), but structurally difficult (the trust story requires the difficulty to be visible). Copy that hides this is worse than copy that names it.

---

## 3. Modal 11.2 — Close confirmation

Same pattern as wf-09 §6.

### 3.1 Copy

| Element | Copy |
|---|---|
| Eyebrow | CONFIRM CLOSE |
| Headline | Close sales now? |
| Body 1 | You're about to freeze the pool at: |
| Body 2 (dynamic) | {total} tickets · {paid} paid · {free} free-route |
| Body 3 | The tickets hash will be computed and published. Sales stop the moment you confirm. |
| Type-to-confirm | Type CLOSE to confirm: |
| Confirm CTA | Close draw |
| Confirm loading | Closing… |
| Cancel | Cancel |
| Fail | Close didn't complete. Try again in a moment. No hash was written and sales are still open. |

Modal mechanics (focus trap, backdrop click = cancel, escape dismisses, idempotency-keyed POST) identical to wf-09 §6.5–6.6.

**The type-to-confirm word is `CLOSE`** — matches the create-flow's `PUBLISH` pattern and the consumer self-exclusion `EXCLUDE`. Single uppercase word, memorable, deliberate friction.

---

## 4. Screen 11.3 — Close receipt

### 4.1 Layout

```
< inside admin shell >

                                                    space.1200

                        ✓                            ← 48pt gold check
                                                        color.brand.accent

                Draw closed.                          ← type.display.section, centered

           ₦2,000,000 in cash draw is                 ← body.default, secondary
                awaiting reveal.

                                                    space.1200

  ┌──────────────────────────────────────────────────────────┐
  │  ▪ CLOSE RECEIPT                                          │  ← gold eyebrow
  │                                                          │      surface.elevated,
  │                                                          │      radius.large,
  │  Draw ID                DRAW-2026-07-08-A                │      elevation.0
  │                                                          │
  │  ─────────────────────────────                            │
  │                                                          │
  │  Tickets hash                                             │  ← label.micro secondary
  │  a7b3e9f1c2...4d82                    📋 Copy full hash  │  ← body.mono 16pt primary
  │                                                          │
  │  ─────────────────────────────                            │
  │                                                          │
  │  Closed at              12 Jul 2026, 19:58:14 WAT         │
  │  Total tickets          1,247                             │
  │  Paid                   1,160                             │
  │  Free-route             87                                │
  │                                                          │
  │  ─────────────────────────────                            │
  │                                                          │
  │  Published to:                                            │
  │  · Consumer draw page — atlas://draw/{draw_id}            │
  │  · Audit log — event `draw.entries_snapshot` #4972       │
  │  · Public /proof endpoint — atlas.ng/proof/{draw_id}     │
  │                                                          │
  │  ─────────────────────────────                            │
  │                                                          │
  │  Reveal fires at        13 Jul 2026, 21:00 WAT            │  ← type.body.emphasis
  │                                                          │      the next scheduled ceremony
  │                                                          │
  │  [ Download receipt (JSON) ]                              │
  └──────────────────────────────────────────────────────────┘

  space.800

  ┌────────────────────────┐  ┌──────────────────────────┐
  │  Go to draw page  →    │  │  View audit log  →       │
  └────────────────────────┘  └──────────────────────────┘

  space.400

  Reveal now (early) →                                        ← inline link, small,
                                                                 only visible if
                                                                 now < scheduled reveal
                                                                 AND early-reveal is
                                                                 permitted by build config
                                                                 (V0.5: true; V1: false)
```

### 4.2 Notes

- **Component reuse:** the receipt structure is intentionally the same pattern as wf-09 §7 (commitment receipt). Same visual language, same download-JSON pattern, same "published to" list. Trust ceremony has a consistent shape.
- **Early-reveal link** exists only for V0.5 demo — allows the founder to demo reveal without waiting for the scheduled time. V1 removes this shortcut; reveal only fires at or after the scheduled reveal time.
- **The "awaiting reveal" state** is now the draw's status until wf-12 fires.

---

## 5. Design invariants for close

1. **Close is always type-to-confirm** — same discipline as create.
2. **The pool count is the last thing shown before confirm** — the modal restates it so the operator sees exactly what they're freezing.
3. **Pending transcriptions surface as a warning, not a hard block** — the operator retains the judgement call, but the queue state is impossible to miss.
4. **`tickets_hash` is the receipt artefact** — computed at close, immutably published, visible to auditor and public alike from that moment on.
5. **The consumer draw page transitions to closed state within the same second** — the trust story requires the operator's action and the consumer visibility to move in lockstep.

---

## 6. Open questions

### For founder:
1. **Manual close in V0.5** vs auto-close at scheduled time (V1). Confirm — the demo will have the founder tap Close in the operator surface as part of the walkthrough?
2. **Early-close window.** Currently the "Closing at" timestamp shows now-ish; if the operator closes ~2 minutes early, no visible fuss. Formal early/late tolerance policy TBD — recommend defer until real operations have data.
3. **Early-reveal link on §4** for the V0.5 demo. Confirm this shortcut is acceptable; if it makes the demo feel like a magic-mode toy, we hide it behind a keyboard shortcut instead of a visible link.

### For ⚖️ Adaeze:
4. **Late-transcription policy** ("intentionally awkward" per §2.4 undo caveat) — what is the specific process? Adaeze — please define, or confirm that the process definition is a runbook rather than a UX artefact.
5. **Free-entry-queue at close — Ignore vs Block.** Currently the queue is a warning, not a block. Alternative: block close if queue > 0. Recommend warning (operator judgement) but confirm.

### For 💻 Amelia:
6. **Ticket-list canonicalization** — JCS (JSON Canonicalization Scheme, RFC 8785) per ADR-006. Confirm the hashing input is exactly `JSON.stringify(sorted_ticket_id_array)` in JCS form and that this is deterministic across Node/Python.
7. **`draw.entries_snapshot` audit-log event shape** — includes `tickets_hash`, `total`, `paid_count`, `free_count`, `closed_at`, `closed_by`. Confirm.

---

## 7. Cross-references

- Flow source: `v0.5-demo-plan.md §2` (step 11).
- Upstream: `09-create-draw.md` (commit), `10-transcribe-free-entry.md` (must be resolved before close).
- Downstream: `12-reveal-draw.md` (the final act of the ceremony).
- Consumer counterpart: `02-browse-active-draw.md §3.3` closed state.
- ADR-006 §Protocol stage 3 — this screen's exact reason to exist.
- Tokens: `tokens.md`.

---

🎨 *End of wireframe 11. Reveal (wf-12) next — same pattern, different content, higher stakes.*

# Wireframe 13 — Audit Log (admin surface)

**Drafted:** 2026-07-08 (Day 10 per `tone-doc.md §8`)
**Drafted by:** 🎨 Sally (BMad UX Designer)
**Status:** Draft — pending founder review + ⚖️ Adaeze compliance review (this is her primary daily surface).
**Covers:** Flagship flow step 13 from `v0.5-demo-plan.md §2` — *"View audit log — filterable table of every recorded event for the draw, chain-verified inline."*
**Surface:** Next.js admin, inside the shell (wf-08 §1).
**Pairs with:** every operator wireframe (this is where the events they produce land), `14-public-proof-page.md` (Day 11 — the consumer/public version of a subset of these events), ADR-005 (hash-chained append-only audit log — this screen's exact reason to exist), ADR-007 §PII redaction (this surface honours the redaction rules), `docs/runbooks/audit-log-chain-break.md` (Tobi's runbook, existing).

---

## 0. What this surface has to prove, every time it renders

Sally's proof pages on the consumer surface (wf-06 §3 reveal, future wf-14 public proof) say to the world: *"here is what happened, here is how you verify."* This screen says the same thing to the operator, plus one more thing:

> *"The record you are looking at has not been tampered with. Here is the current chain head. Here is when it was last independently verified. Here is what would happen if any row were changed."*

The trust story on this screen is not primarily about *what happened* — every event's payload does that. It is about **the integrity of the record itself.** A tampered audit log is worse than no audit log; it produces confident wrong answers. So this surface must:

1. Show, at the top of the page, the current state of the chain (head hash, sequence, last-verified time). If the nightly verifier has flagged a break, that state is loud and immovable.
2. For each row: show the row's hash and its previous-hash, and let the operator visually confirm they chain. Not a demand — a demonstration.
3. Reveal the payload without exposing PII by default (redacted per ADR-007). PII expansion is an explicit action, per-row, audit-logged.
4. Never offer an edit, delete, or "correct" affordance. Even for typo fixes. The log is what happened.
5. Export completely and reproducibly. Same input → identical export bytes, so third parties can hash and compare.

Everything below serves those five commitments.

**Non-goals for V0.5:**
- Real-time streaming updates (WebSocket / SSE). V0.5 refreshes via pull-to-refresh or explicit reload; V1 gets live updates.
- Log search across multiple projects / tenants. Atlas is single-tenant in V0.5 and V1.
- Automated anomaly detection ("unusual pattern flagged"). V2.
- Multi-user commentary on events (annotations, review notes). V1 for Adaeze's own workflow; V0.5 skips.
- Cryptographic proof export as a signed bundle (regulator hands you a bundle and can offline-verify against Atlas's public key). Deferred — the JSON export is enough for V0.5, the signed variant is a V1+ concern with counsel input on regulatory expectations.

---

## 1. Where in the shell

Sidebar → **REVIEW → Audit log**.

Default view: current draw's events (if a draw is active or recently-revealed), most recent first. Filters below let the operator narrow by event type, actor, date range, or subject.

---

## 2. Screen 13.1 — Audit log index (the primary surface)

### 2.1 Layout

```
< inside admin shell >

  Audit log

                                                       [ Export JSON ] [ Export CSV ]

  space.400

  ┌──────────────────────────────────────────────────────────┐
  │  ▪ CHAIN STATE                                            │  ← ChainStateBanner
  │                                                          │      surface.elevated
  │  ✓ Chain intact                                           │      radius.large
  │                                                          │      elevation.0
  │  Head hash    d4a7f1e6b9...02c8       📋                 │      body.mono for hashes
  │  Sequence     #5013                                       │
  │  Last verified 13 Jul 2026, 03:00:00 WAT                  │
  │                by nightly verifier                        │
  │                                                          │
  │  [ Re-verify now ]                                        │  ← inline button
  └──────────────────────────────────────────────────────────┘

  space.600

  ┌──────────────────────────────────────────────────────────┐
  │  ▪ FILTERS                                                │  ← filter row card
  │                                                          │
  │  Draw    [ DRAW-2026-07-08-A                        ▾ ]  │  ← dropdown
  │                                                          │
  │  Event   [ All events                               ▾ ]  │  ← multi-select dropdown
  │                                                          │
  │  Actor   [ Any                                      ▾ ]  │  ← dropdown
  │                                                          │
  │  From    [ 08 Jul 2026, 00:00 ]                          │  ← date-range pickers
  │  To      [ Now                 ]                          │
  │                                                          │
  │  Subject [ Any type ▾ ] [ ID search…              ]      │
  │                                                          │
  │  [ Reset filters ]                       [ Apply ]        │
  └──────────────────────────────────────────────────────────┘

  space.600

  1,247 events · showing 25 most recent · sequence 4988..5013

  ┌────┬──────────────────┬─────────────┬───────────────┬──────────────────┬────────┐
  │ #  │ Time (WAT)       │ Event       │ Subject       │ Actor            │ Chain  │
  ├────┼──────────────────┼─────────────┼───────────────┼──────────────────┼────────┤
  │5013│ 13 Jul 21:06:44  │ draw.winner │ ticket 04829  │ system           │  ✓     │
  │    │                  │  _selected  │               │                  │        │
  │5012│ 13 Jul 21:06:41  │ draw.       │ DRAW-...-A    │ operator         │  ✓     │
  │    │                  │  revealed   │               │  Adaobi Ibe      │        │
  │5011│ 13 Jul 21:06:39  │ notification│ ticket 04829  │ system           │  ✓     │
  │    │                  │  .sent      │               │                  │        │
  │... │                                                                     │        │
  │4988│ 08 Jul 13:47:52  │ draw.       │ DRAW-...-A    │ operator         │  ✓     │
  │    │                  │  committed  │               │  Adaobi Ibe      │        │
  └────┴──────────────────┴─────────────┴───────────────┴──────────────────┴────────┘

  Each row is clickable → opens Screen 13.2 (event detail).

  space.600

  [ ← Older ]                                              [ Newer → ]

                            (pagination — 25 per page)
```

### 2.2 Components used

- `AdminPageHeader` (headline + trailing action buttons for export — first appearance of export on an admin surface).
- `ChainStateBanner` — new; the *load-bearing* component of this surface. Composition: chain-state icon (`✓ intact` / `⚠ verification pending` / `⌀ BROKEN`) + head hash with copy affordance + sequence number + last-verified metadata + a `Re-verify now` inline button. **This component is what makes the audit-integrity story visible on the surface itself.**
- `FilterCard` — new; a bordered card holding filter controls, always visible above the table. Draws dropdown (defaulted to current), event multi-select, actor filter, date range, subject lookup, reset + apply.
- `AuditRowTable` — new; the data table. Columns: seq (mono), time (WAT), event (kebab-case event name in mono), subject (subject_type + ID; truncated with copy affordance on hover), actor (name if known, `system` for automated events), chain state (`✓` per-row indicator).
- `Pagination` — 25 rows per page; Older / Newer navigation. Newest-first ordering.
- `Button` — Export JSON and Export CSV as secondary buttons top-right.

### 2.3 States

**Chain intact (default):** ChainStateBanner shows the `✓ Chain intact` state in `color.state.success` on `surface.elevated`. The tone is calm — no celebration, no fanfare. The banner should read as *"working as expected"*, not as a boast.

**Verification pending (verifier hasn't run recently — > 24h since last check):** banner shifts to `color.state.attention`. Copy: *"Verification pending — last run {time}. Re-verify now."*

**Chain BROKEN (nightly verifier detected a hash mismatch):** banner becomes prominent and immovable. Full-width, `color.state.danger` 4pt left border, solid `state.danger` icon, headline *"⌀ CHAIN INTEGRITY BROKEN"*, body describing which sequence range fails to chain, and a hard link to `docs/runbooks/audit-log-chain-break.md` (Tobi's runbook). No dismissal option. **Table rows below still render, but a per-row visual cue appears on any row inside the broken range** (dark orange row border + a warning icon replacing the row's chain-state tick).

Adaeze must see this state loud and clear the moment she loads the surface; there is no scenario where a broken chain is acceptable, so no scenario where the banner is muted.

**Verification in progress (re-verify tapped):** banner temporarily replaces the state with `⋯ Re-verifying…` and a progress indicator (verification is fast — hundreds of thousands of rows in seconds). Re-completes to the new state.

**Filter applied:** the table narrows; the count line updates (*"1,247 events · showing 12 filtered · sequence 4990..5012, non-contiguous"* — the "non-contiguous" wording is important, it tells the operator they're not looking at a contiguous chain window). Filters persist in the URL query string so the operator can bookmark or share a filtered view.

**Empty (no events match filter):** table replaced by centered copy *"No events match these filters. Try widening the range or resetting."*

**Loading (initial fetch):** skeleton table rows shimmer.

**Error (fetch failed):** banner: *"Couldn't load the audit log. Reload the page or try again in a moment."*

### 2.4 Copy

| Element | Copy |
|---|---|
| Page headline | Audit log |
| Export JSON CTA | Export JSON |
| Export CSV CTA | Export CSV |
| Chain state eyebrow | CHAIN STATE |
| Chain intact | ✓ Chain intact |
| Chain intact — head label | Head hash |
| Chain intact — seq label | Sequence |
| Chain intact — verified label | Last verified {timestamp} by nightly verifier |
| Chain verification pending | ⚠ Verification pending — last run {time}. |
| Chain BROKEN — heading | ⌀ CHAIN INTEGRITY BROKEN |
| Chain BROKEN — body | Sequences {start}–{end} do not chain to expected hashes. This means the audit log has been modified since the last verification, or a bug in ingestion has corrupted the chain. **Do not treat any event as reliable until Compliance & Engineering have investigated.** Runbook: {runbook_url}. |
| Re-verify button | Re-verify now |
| Re-verifying state | ⋯ Re-verifying… |
| Filters eyebrow | FILTERS |
| Draw filter label | Draw |
| Event filter label | Event |
| Actor filter label | Actor |
| From label | From |
| To label | To |
| Subject filter label | Subject |
| Reset filters | Reset filters |
| Apply | Apply |
| Count line — default | {total} events · showing {n} most recent · sequence {start}..{end} |
| Count line — filtered | {total} events · showing {n} filtered · sequence {start}..{end}, non-contiguous |
| Empty | No events match these filters. Try widening the range or resetting. |
| Table col — # | # |
| Table col — Time | Time (WAT) |
| Table col — Event | Event |
| Table col — Subject | Subject |
| Table col — Actor | Actor |
| Table col — Chain | Chain |
| Older | ← Older |
| Newer | Newer → |
| Error banner | Couldn't load the audit log. Reload the page or try again in a moment. |

**Copy commentary:**

- *"Do not treat any event as reliable until Compliance & Engineering have investigated"* — this is the strongest sentence in the whole product. It appears once, only on the chain-broken state, only when it is true. Copy that assertive works because the underlying condition is rare and serious.
- The count-line *"non-contiguous"* language on filtered views is a small but important integrity cue — a filtered view is showing you a *sample*, not a *chain*; the operator should not read row N+1 as chaining from row N in a filtered view.

### 2.5 Accessibility

- **Focus order:** headline → Export buttons → ChainStateBanner (composite; Re-verify button focusable) → FilterCard (each control) → Reset + Apply → count line (non-focusable) → table rows (each row focusable as a link to detail) → pagination.
- **ChainStateBanner:** `role="status"` in intact state; `role="alert"` in broken state. Broken state announced first on page load.
- **Table:** proper `<table>` with `<thead>` and column `<th scope="col">`. Rows are focusable via keyboard (`tabindex="0"`); Enter opens detail. Sort not offered in V0.5 (default sort is seq desc; no user re-sort).
- **Hash cells** are read as *"row hash d 4 a 7 truncated 0 2 c 8"* — a screen reader user gets the truncation cue explicitly. Copy-full-hash affordance available on hover/focus.
- **Filter dropdowns:** ARIA combobox pattern; multi-select event filter announces selection changes.
- **Contrast:** all tokens as spec. Broken-chain state uses `color.state.danger` at full contrast.
- **Reduce motion:** re-verification progress uses a static spinner glyph instead of an animated one.

### 2.6 Interaction

- **Row click:** opens Screen 13.2 (event detail) in a side panel (below §3), not a new page. Table remains visible; operator can navigate between rows without losing context.
- **Copy head hash:** copies to clipboard, toast *"Head hash copied."*
- **Re-verify now:** triggers server-side re-run of the chain verification. Duration typically < 5 seconds even for large logs. On completion, updates the banner with the new verified-at timestamp.
- **Filter apply:** updates URL query string (bookmarkable); table refetches with filter parameters.
- **Export JSON / CSV:** triggers download. See §4.

---

## 3. Screen 13.2 — Event detail (side panel)

### 3.1 Layout (slides in from right, ~ 40% viewport width)

```
< side panel over admin shell, elevation.2 backdrop >

  ┌──────────────────────────────────────────────────────────┐
  │ #5012 · draw.revealed                            [ ✕ ]   │  ← panel header
  │                                                          │      body.mono for event name
  ├──────────────────────────────────────────────────────────┤
  │                                                          │
  │  ▪ EVENT                                                  │  ← gold eyebrow
  │                                                          │
  │  Occurred       13 Jul 2026, 21:06:41.284 WAT             │  ← body.default
  │  Event          draw.revealed                             │  ← body.mono
  │  Subject        draw · DRAW-2026-07-08-A                  │
  │  Actor          operator · Adaobi Ibe (id ...)            │
  │                                                          │
  │  ─────────────────────────────                            │
  │                                                          │
  │  ▪ CHAIN                                                  │
  │                                                          │
  │  Sequence       #5012                                     │
  │  Prev hash      a3f9c1b7...84e2       📋                 │  ← body.mono
  │  Row hash       d4a7f1e6...02c8       📋                 │
  │                                                          │
  │  ✓ This row chains to sequence #5011.                     │  ← per-row inline check
  │                                                          │      body.small state.success
  │  [ Re-verify chain from this row ]                        │  ← inline button
  │                                                          │
  │  ─────────────────────────────                            │
  │                                                          │
  │  ▪ PAYLOAD                                                │
  │                                                          │
  │  ⓘ Payload is redacted per ADR-007. Fields marked ●●●     │  ← body.small secondary
  │    contain PII. Reveal only with cause — reveals are      │
  │    themselves audit-logged.                                │
  │                                                          │
  │  ┌────────────────────────────────────────────────────┐ │
  │  │ {                                                  │ │  ← body.mono
  │  │   "draw_id": "DRAW-2026-07-08-A",                  │ │      pretty-printed JSON
  │  │   "revealed_at": "2026-07-13T20:06:41.284Z",       │ │      13pt line-height 1.5
  │  │   "server_seed": "9e014b7d...4c67",                │ │
  │  │   "bitcoin_block": 856142,                          │ │
  │  │   "bitcoin_hash": "8f1c3e9f...9e42",               │ │
  │  │   "drand_round": 4829301,                          │ │
  │  │   "drand_randomness": "3b7d02a4...0c88",           │ │
  │  │   "tickets_hash": "a7b3e9f1...4d82",               │ │
  │  │   "winning_ticket": "04829",                        │ │
  │  │   "reserves": ["07213","00042","03917",             │ │
  │  │                "06104","01288"],                    │ │
  │  │   "winner_owner_id": "●●● [ Reveal ]",              │ │  ← redacted PII
  │  │   "winner_contact": "●●● [ Reveal ]"                │ │
  │  │ }                                                   │ │
  │  └────────────────────────────────────────────────────┘ │
  │                                                          │
  │  [ Copy payload JSON ]  [ Reveal all PII ]               │  ← two actions
  │                                                          │
  │  ─────────────────────────────                            │
  │                                                          │
  │  ▪ RELATED                                                │
  │                                                          │
  │  · #5013 · draw.winner_selected   (next in chain)        │  ← links to related events
  │  · #5011 · notification.sent      (immediately prior)     │
  │  · #4988 · draw.committed         (draw lifecycle root)   │
  │                                                          │
  │  ─────────────────────────────                            │
  │                                                          │
  │  [ Close panel ]                                          │
  └──────────────────────────────────────────────────────────┘
```

### 3.2 Components used

- `SidePanel` — new; slides in from right, focus-trapped, closes via `✕`, backdrop, or escape.
- `SectionLabel` (gold eyebrow — reused).
- `DefinitionList` (reused).
- `HashRow` (reused from consumer surface).
- `PayloadViewer` — new; a bordered container with syntax-lit pretty-printed JSON. PII fields render as `●●● [ Reveal ]` unless expanded. Reveal actions are per-field or all-at-once.
- `RelatedEventsList` — new; a short list of contextually related events (adjacent in sequence, related by subject, related by lifecycle stage). Each item is a link that opens the target event in the same side panel.
- `Button` (secondary variants).

### 3.3 States

**Default (payload redacted):** as drawn. PII fields hidden.

**Payload fully revealed:** all `●●●` fields expanded to their real values. **A `payload.pii_revealed` audit-log event is written** with the revealing operator + the specific fields exposed + the reason (if operator supplied one via a prompt). This is the self-referential audit-log-of-audit-log-access — Adaeze's rule from REVIEW-001 §5.9.4 (S3 access logs) applied to the log itself.

**Per-field reveal:** the specific `[ Reveal ]` tapped expands only that field. Same audit event written.

**Chain check inline:** on side-panel open, the client re-hashes this row and compares to server-stored `row_hash`. Passes → `✓ This row chains to sequence #{prev}.` Fails → `⌀ Chain check failed for this row.` in danger + prominent alert (bug or tampering).

**Related-events tapped:** panel updates to show the newly-selected event; a small back-arrow appears in the panel header. Operator can navigate a chain of related events without leaving the panel context.

### 3.4 Copy

| Element | Copy |
|---|---|
| Panel header | #{seq} · {event_name} |
| Section eyebrow — event | EVENT |
| Occurred label | Occurred |
| Event label | Event |
| Subject label | Subject |
| Actor label | Actor |
| Section eyebrow — chain | CHAIN |
| Sequence label | Sequence |
| Prev hash label | Prev hash |
| Row hash label | Row hash |
| Chain intact inline | ✓ This row chains to sequence #{prev_seq}. |
| Chain broken inline | ⌀ Chain check failed for this row. Prev-hash does not match sequence #{prev_seq}'s row-hash. |
| Re-verify chain | Re-verify chain from this row |
| Section eyebrow — payload | PAYLOAD |
| Redaction note | Payload is redacted per ADR-007. Fields marked ●●● contain PII. Reveal only with cause — reveals are themselves audit-logged. |
| Reveal action (per field) | [ Reveal ] |
| Reveal all action | Reveal all PII |
| Reveal-all prompt | You're about to reveal PII fields ({field_names}) on event #{seq}. This action is audit-logged with your identity. Reason: |
| Reveal-all prompt input placeholder | e.g. "Investigating claim CL-04829-6JQ7" |
| Reveal-all confirm | Reveal |
| Reveal toast | PII revealed. Access recorded as audit event #{new_seq}. |
| Copy payload | Copy payload JSON |
| Copy payload toast | Payload copied. |
| Section eyebrow — related | RELATED |
| Related items | · #{seq} · {event_name}   ({context}) |
| Close panel | Close panel |

### 3.5 Accessibility

- **Panel semantics:** `role="dialog"` `aria-modal="true"` `aria-labelledby="panel-header"`.
- **Focus trap:** focus enters panel on open; Escape / backdrop / Close returns focus to the originating table row.
- **Chain-check inline:** state announced via `aria-live="polite"` on state change.
- **Payload JSON:** rendered inside `<pre>` with `role="region"` and a label; screen reader users can enter code-mode.
- **Reveal actions:** the `[ Reveal ]` chip inside redacted fields has `aria-label="Reveal PII field {field_name}. Reveals are audit-logged."`
- **Reveal prompt modal:** the reason-input is required (empty reason blocks the reveal); focus lands on the input on open.

### 3.6 Interaction

- **Row click on the index table:** slides panel in. Table remains behind (partial visibility) so operator can navigate the table with keyboard.
- **Reveal (per field or all):** on reveal, a small modal asks for a `reason` string (required for `Reveal all`; optional for per-field but strongly encouraged). Submit fires `POST /admin/audit-log/reveal` which returns the un-redacted values AND writes the meta-audit-event.
- **Copy payload JSON:** copies the *currently-visible* payload (redacted or expanded). If PII is redacted, the copied text shows `●●●` placeholders — a small but real integrity cue.
- **Re-verify chain from this row:** triggers a targeted verification (from this row forward). Useful for confirming a specific range without re-running the whole chain.
- **Related events:** tapping updates the panel in place (no separate page load). Panel header gains a back-arrow to return to the previous event.

---

## 4. Export

### 4.1 Export JSON

Downloads a single JSON file containing (a) chain-state header (head hash, sequence, verified-at) and (b) every event in scope. Fields:

```json
{
  "chain_state": {
    "head_hash": "...",
    "sequence": 5013,
    "last_verified_at": "..."
  },
  "filters_applied": { ... },
  "generated_at": "...",
  "generated_by": "operator/{operator_id}",
  "event_count": 1247,
  "events": [ { "seq": 1, "prev_hash": "GENESIS", "row_hash": "...", "occurred_at": "...", ... }, ... ]
}
```

**Redaction discipline:** exported JSON respects the same PII redaction as the on-screen payload viewer. To export **un-redacted** PII, the operator must tap `Export JSON (unredacted)` — a separate action, guarded by a type-to-confirm modal (word: `EXPORT`) that fires a `data.exported` audit event with the operator + reason.

Deterministic canonicalization: the same filter + same log state produces byte-identical exports, so a third party can hash the export and get the same hash Atlas would.

### 4.2 Export CSV

Same content but flattened for spreadsheet consumption. PII redacted by default; un-redacted export gated the same way.

### 4.3 Verifier command hint

At the bottom of the exports drop-down: a small line reads: *"To verify a downloaded JSON export locally, run: `python -m atlas.verify --audit-export {file}`"* — same discipline as the reveal-receipt verifier command in wf-12 §6.

---

## 5. Design invariants for the audit log

Recording explicitly because this surface is Adaeze's daily home and any drift will hurt her most:

1. **The audit log is never editable on this surface.** No edit, no delete, no "correct typo". Read-only forever.
2. **Chain state is always visible at the top of the page.** No collapsed/hidden variant.
3. **Broken chain state is immovable and loud.** No dismissal, no muting.
4. **PII is redacted by default, revealed only with cause, and every reveal is itself audit-logged.**
5. **Filtered views are marked as non-contiguous** so they aren't mistakenly treated as chain segments.
6. **Every export is deterministic** — same input produces byte-identical output.
7. **Un-redacted export is a separate, gated action.** Never the default.
8. **Related-events navigation happens in-panel** — the operator doesn't lose their table position when exploring context.

---

## 6. Open questions

### For founder:
1. **Export CSV in V0.5.** Adds one more format to maintain; some regulator/auditor workflows do expect CSV. Recommend keep both.
2. **Un-redacted export requiring type-to-confirm `EXPORT`.** The reveal-word inflation (`PUBLISH`, `CLOSE`, `REVEAL`, now `EXPORT`) is a small tax. If it feels over-templated, we can drop this one back to a single-confirm modal (since export is less-consequential than the ceremony actions).

### For ⚖️ Adaeze — this is your surface, largest ask:
3. **Chain-state banner language and visual weight.** Is the *"Do not treat any event as reliable until Compliance & Engineering have investigated"* sentence too strong, correct, or too weak for the broken-chain state? Your call.
4. **Redaction defaults.** ADR-007 §PII redaction covers KYC responses; this surface generalises the principle to any PII in any event payload. Confirm the defaults are right (BVN, contact info, ID document references redacted; ticket IDs, hashes, timestamps, event names in plain).
5. **Reveal-with-reason prompt.** Is a free-text reason acceptable, or do you want a fixed set of reason codes (`investigation`, `claim_review`, `compliance_audit`, `other`)? Recommend fixed codes with an optional free-text elaboration; that pattern makes retro-analysis of reveal patterns tractable.
6. **Meta-audit-event granularity.** Every PII reveal writes an event. Every export writes an event. Every re-verification writes an event. Is this the right granularity, or is it noise?
7. **Retention.** How long does the audit log itself retain? ADR-005 doesn't set a retention period. Legal position — likely no retention limit for prize-competition audit records, but confirm.
8. **Regulator access mode.** Is there a "read-only regulator role" that would land on this surface in V1? If yes, the RBAC surface (per plan §3, deferred to Phase 3) needs to accommodate.
9. **Export sign-off.** Should un-redacted exports carry a cryptographic signature from a signing key held by Compliance, so a regulator can prove the export they received is authentic and unmodified? V1+ concern with counsel input.

### For 💻 Amelia:
10. **Chain-check-in-client on side-panel open** (§3.3). The client independently re-hashes the row and compares to server-supplied `row_hash`. This is a defense-in-depth against a server bug that reports the wrong hash. Confirm it's feasible for the client to have the JCS canonicalizer.
11. **Re-verify performance.** The nightly job re-hashes the full log; the on-demand `Re-verify now` needs to complete in seconds. If the log grows large enough that this becomes a problem, we chunk it. Confirm the log size projection for V0.5 and V1.
12. **Filter param format** in URL for bookmarkability. Suggested: `?draw={id}&event=draw.committed,draw.revealed&from={iso}&to={iso}`.
13. **Export streaming.** For very large exports, stream rather than build in memory. V0.5 log is small; V1 concern.

### For 🛡️ Tobi:
14. **Runbook `docs/runbooks/audit-log-chain-break.md`** — exists per scaffold. Confirm it covers: (a) how to identify the tampering vs bug distinction, (b) recovery steps if it was a bug, (c) escalation if it was a real tampering event.
15. **Nightly verifier job** — cron schedule, alert routing on failure, retention of verifier run history.

---

## 7. Cross-references

- Flow source: `v0.5-demo-plan.md §2` (step 13).
- Source of every event: every operator wireframe (`09`, `10`, `11`, `12`) plus consumer flows via the outbox pattern (ADR-002).
- Consumer counterpart: `14-public-proof-page.md` (Day 11) — a subset of these events, public-facing.
- ADR-005 — this screen's exact reason to exist.
- ADR-007 §PII redaction — the redaction rules this surface honours.
- Runbook: `docs/runbooks/audit-log-chain-break.md` (Tobi).
- Compliance review: `docs/compliance/reviews/REVIEW-001-v0.5-consumer-wireframes.md` (Adaeze) — the audit-log invariants inform this surface's design.
- Tokens: `tokens.md`.

---

🎨 *End of wireframe 13. Day 10 complete.*

*This is Adaeze's primary daily surface. She should walk it before Day 11 begins — if the chain-state treatment or the PII-redaction discipline needs work, better to catch it now than after the public proof page (wf-14) uses the same visual language.*

*Day 11 tomorrow — the wow moment. The public proof page is where all the trust-story artefacts from wf-09 (commit), wf-11 (close), wf-12 (reveal), and a subset of this audit log land as one page that anyone in the world can visit and verify. Per REVIEW-001 §6.4 I'll route the working draft to Adaeze early, not polished.*

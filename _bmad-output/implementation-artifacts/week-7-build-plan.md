# Week 7 Build Plan — Public proof page + polish + demo-mode + exit gates

**Drafted:** 2026-07-29 (Week 6 close; Week 7 kickoff on founder sign-off)
**Drafted by:** 💻 Amelia (BMad Dev)
**Status:** **Draft — pending founder decisions on §9 asks.**
**Applies to:** V0.5 investor demo finale — the last mile.
**Pairs with:** `v0.5-demo-plan.md §5 Week 7`, `week-6-build-plan.md` (foundation: full draw engine + proof + verifier), all wireframes.

---

## 1. Scope

**In.**

- **Demo-mode config**: `ATLAS_DEMO_MODE=true` compresses the seeded draw's `close_time` to `seed_time + 3 min` and `draw_time` to `seed_time + 4 min` so the pitch doesn't wait days. Production defaults false. Config validator refuses `demo_mode=true` when `env=production`.
- **`make demo-reset`** upgraded — wipes DB volume, re-applies all migrations, re-runs `seed_v0_5.py` (draw + questions), re-runs `bootstrap_superadmin.py`. Target: < 30s per `v0.5-demo-plan.md §6`.
- **Fresh-clone drill v5**: `git clone && make setup && make dev && make demo-reset && make demo-open-browser` — the last target opens the public proof page + admin login in the founder's browser. Timed target < 15 min.
- **Public proof page** (Next.js SSR at `/proof/[drawId]`) — reads `GET /proof`, renders the trust surface: commitment, revealed inputs, winners (position + user_id_hash + ticket_id short), copy-paste verifier command. The demo wow-moment.
- **Trust-story pages** (static Next.js):
  - `/how-it-works` — prize-competition explainer per `v0.5-demo-plan.md §2.15`.
  - `/responsible-play` — self-exclusion mention per §2.16.
- **Admin Next.js pages** — minimum viable so the founder demos via buttons, not curl:
  - `/admin/draws` — list + create draw form.
  - `/admin/draws/[id]` — draw detail + close button + reveal button + winners table.
  - `/admin/free-entry` — transcribe slip form.
  - `/admin/audit-log` — filterable audit-log table (per demo plan §2.13).
- **Mobile Flutter surfaces** — the hero flow. `browse` + `skill-question` + `checkout-webview` + `my-tickets` + `winner-notification` screens. Home screen (identity/home from Week 3) extended with the wallet chip + active-draw card.
- **Winner-claim minimum:** `POST /api/v1/draws/{draw_id}/winners/{ticket_id}/claim` (backend) + mobile "Claim your prize" screen showing "claim received" state. `contact_status` advances `pending → contacted → claimed`.
- **Screen-recording script**: a Playwright script that auto-plays the flagship-flow (register → skill → pay → close → reveal → verify) so the founder has a fallback if live-share fails during a pitch.
- **AI Integration Log entries** for Weeks 3-7 (owed by Paige/Amelia — Week 7 closes the loop).

**Out** (V1 hardening, not V0.5 demo):

- Real WhatsApp notification (V1).
- Multi-draw browse (V1 — V0.5 shows one active draw).
- Prize-claim state machine beyond `pending → contacted → claimed` (V1).
- Refund UX (V1).
- Admin RBAC beyond superadmin + user (V1 — full 5-role split).
- Observability stack (Sentry, structured logging aggregation) — Phase 5.
- Sentry / error monitoring — Phase 5.

---

## 2. Day-by-day breakdown

### Day 1 (Mon 2026-08-11) — Demo-mode config + demo-reset + winner-claim backend

- `atlas.config.demo_mode: bool = False`. Prod validator: refuses `demo_mode=true` when `env=production`.
- `seed_v0_5.py` reads `demo_mode`: when true, sets `close_time = now + 3min`, `draw_time = now + 4min`. When false (dev/prod), keeps the current 3-day window.
- `make demo-reset` extended: wipe volume → migrate → seed → bootstrap. Timed check must land < 30s (compose start is separate).
- `POST /api/v1/draws/{draw_id}/winners/{ticket_id}/claim` — winner-only endpoint (must be the user_id on the winner row). Marks `contact_status='claimed'`. Emits `draw.winner_claimed` audit event.
- Migration 0010: no schema changes — reuse `draw_winners.contact_status` from W6. Skip migration this day.
- Tests: demo-mode timing math; claim endpoint happy + 403 (non-winner) + 404 (unknown winner) + 409 (already claimed).

**Demoable EOD:** `make demo-reset` cold-cycles < 30s; sales_open draw has close 3 min in future.

### Day 2 (Tue) — Public proof page (Next.js)

- `admin/src/app/(public)/proof/[drawId]/page.tsx` — server-rendered. Fetches `GET /proof` at request time. Renders:
  - Header with draw prize + state badge.
  - Commitment (verbatim, monospace).
  - Post-reveal grid: server_seed, tickets_hash, bitcoin block (with height + link to mempool.space at that height), drand round + randomness.
  - Winners table (position, is_primary, ticket_id short, user_id_hash short).
  - "Verify this yourself" block: copy-button with the exact `python backend/tools/verify_draw.py --proof-url ...` command.
  - Link to `docs/adr/ADR-006` (GitHub) as algorithm reference.
- Zero JS on first paint (SSR only, hydration for the copy button). Accessible. Prints cleanly for regulator screenshots.
- Public — no auth required, no cookies read.
- Playwright test: page loads, contains all field labels, copy-button click writes to clipboard.

**Demoable EOD:** browse `http://localhost:3000/proof/{draw_id}` after `make demo-close-reveal` — all trust-story fields visible.

### Day 3 (Wed) — Trust-story pages + mobile browse/skill/tickets

- `admin/src/app/(public)/how-it-works/page.tsx` + `/responsible-play/page.tsx`. Static, no auth, no DB. Copy from `v0.5-demo-plan.md §2.15-16`.
- Mobile Flutter:
  - `home` extended: wallet chip (reads `GET /users/me/wallet`) + active-draw card (reads `GET /draws` and picks the one open draw).
  - `draw_detail` screen: prize copy, timer to close_time, "Enter for ₦500" button.
  - `skill_question` screen: reads `GET /draws/{id}/skill-questions/next`, submits answer.
  - `checkout_webview` screen: opens the Paystack `checkout_url` in an in-app browser; on success returns to app; on failure retry.
  - `my_tickets` screen: reads `GET /tickets/me`, renders as list with entry_source badge (paid vs free).
- Sally handoff: wireframes 02, 04, 05, 10 — confirm the copy still matches implementation.

**Demoable EOD:** Flutter app on iOS simulator: log in → home → tap the draw card → skill question → correct answer → checkout webview opens on mock URL → tickets tab shows the pending purchase.

### Day 4 (Thu) — Admin Next.js pages

- `admin/src/app/(admin)/draws/page.tsx` — list active draws + "Create draw" CTA modal (form: prize_copy, ticket_price_minor, close_time, draw_time).
- `admin/src/app/(admin)/draws/[id]/page.tsx` — draw detail: state badge, tickets_hash, close-button (state=sales_open), reveal-button (state=sales_closed), winners table (state=revealed).
- `admin/src/app/(admin)/free-entry/page.tsx` — form: draw picker + subject user (email lookup) + slip_reference field → POST /tickets/free.
- `admin/src/app/(admin)/audit-log/page.tsx` — paginated table with event_name filter + subject_type filter + date range. Reads a new `GET /api/v1/audit-log` endpoint (backend — needs to add). Chain-integrity badge per row.
- Backend: `GET /api/v1/audit-log?event_name=&subject_type=&since=&until=&limit=` — admin-only. Returns audit events + chain-verification result per page.
- Backend: `GET /api/v1/users?email=` — admin-only email lookup for the free-entry form.

**Demoable EOD:** admin logs in → creates a fresh draw → the founder buys a ticket from mobile → admin closes → admin reveals → winners table shows the primary + reserves.

### Day 5 (Fri) — Winner claim UI + screen recording + full rehearsal + Week 7 exit gates

- Mobile: `winner_notification` screen — reads `GET /tickets/me` filtered to winners; shows "You won!" for primary, "Reserve #N" for reserves. "Claim" button posts to `POST /draws/{id}/winners/{ticket_id}/claim`. "Claim received" confirmation.
- Playwright screen-recording script: `infrastructure/scripts/record_demo.py`. Drives the full flagship-flow through the browser. Saves an mp4 to `_bmad-output/demo/atlas-hero-flow.mp4`. Fallback if live-share fails.
- Full flagship-flow rehearsal — Amelia walks through all 16 steps end-to-end and files any friction as GitHub issues.
- Week 7 exit gates verified (§8).
- AI Integration Log entries backfilled for Weeks 3-7.

**Demoable EOW:** the founder walks steps 1-16 on a clean laptop in < 5 minutes without a stumble. Every step from `v0.5-demo-plan.md §2` runs green. Screen recording exists as fallback.

---

## 3. Module contracts

### 3.1 New backend endpoints

| Method | Path | Idempotency | Auth |
|---|---|---|---|
| `POST` | `/api/v1/draws/{draw_id}/winners/{ticket_id}/claim` | required | winner user only |
| `GET` | `/api/v1/audit-log` | n/a | superadmin |
| `GET` | `/api/v1/users?email=` | n/a | superadmin |

### 3.2 Public routes (Next.js, no auth)

| Path | Description |
|---|---|
| `/proof/[drawId]` | The trust-story page — server-rendered. |
| `/how-it-works` | Prize-competition explainer. |
| `/responsible-play` | Self-exclusion mention. |

### 3.3 Admin routes (Next.js, superadmin only)

| Path | Description |
|---|---|
| `/admin/draws` | List + create. |
| `/admin/draws/[id]` | Detail + close/reveal buttons + winners. |
| `/admin/free-entry` | Transcribe slip form. |
| `/admin/audit-log` | Filterable audit-log table. |

### 3.4 Mobile Flutter screens

- `home` (extended): wallet chip + active-draw card.
- `draw_detail` — prize + timer + Enter button.
- `skill_question` — GET next + POST answer.
- `checkout_webview` — Paystack (stub URL) in-app.
- `my_tickets` — list.
- `winner_notification` — if user has a winner row, prominent CTA to claim.

### 3.5 Module boundary invariants (extend W6 §3.4)

- Public proof page uses no admin/user session — the endpoint is public. Playwright test asserts a request without cookies works.
- `POST /claim` verifies `draw_winners.user_id == current_session.user_id`. Non-winner → 403.
- Admin pages behind the existing session cookie gate + superadmin RBAC.

---

## 4. Test strategy (for Murat 🧪)

**Backend:**
- Existing 241 tests continue to pass.
- Add: claim endpoint happy path + 403 non-winner + 409 already-claimed; audit-log filter endpoint; user email-lookup endpoint.

**Frontend:**
- Public proof page: Playwright snapshot test for pre-reveal + post-reveal states. Copy-button interaction.
- Admin pages: happy-path Playwright walks (login → create draw → close → reveal).
- Mobile: Flutter widget tests for the new screens (already scaffolded from Week 3 Day 3 primitives).

**E2E (Day 5):**
- Rehearsal script + Playwright recording IS the end-to-end validation for the demo.

**Not in Week 7:**
- Load testing (V1).
- Multi-draw scenarios (V1).

---

## 5. Handoffs and dependencies

### To 🎨 Sally (UX)

- **Days 2-4 blocking:** confirm the design tokens + copy still match what wireframes 02, 04, 05, 10, 11, 12, 13, 14 specify. Any drift → Sally updates the wireframe + Amelia matches.
- **Day 2 blocking (small):** the public proof page has no wireframe — Sally sketches one Monday. V0.5 uses a functional-first layout; production polish is V1.

### To 🛡️ Tobi (DevSecOps)

- **Day 1 blocking:** confirm `make demo-reset` timing target of < 30s is realistic in the local Docker environment. If not, relax to < 60s.
- **Day 5 non-blocking:** Playwright recording infrastructure — should the mp4 land in `_bmad-output/demo/` or a separate `demo-assets` folder?

### To 🏗️ Winston (Architect)

- **Day 4 blocking (small):** the `GET /audit-log` filter endpoint — confirm the chain-verification-per-page approach vs a batch verification on request.

### To ⚖️ Adaeze (Compliance & Risk)

- **Day 2 blocking-ish:** the public proof page content — confirm no regulatory red flags. Recommend "provably fair" + link to ADR-006 + verifier command.
- **Day 3 blocking-ish:** trust-story pages copy — confirm the language avoids "lottery" and stays "prize competition + free entry route".
- **Day 5 non-blocking:** end-to-end demo review from a compliance lens.

---

## 6. Risks

Ranked by likelihood × slip-impact.

1. **Frontend scope creep (Days 2-4, high likelihood, half-day to full-day slip per surface).** Next.js + Flutter both take longer per feature than backend. If we slip on admin pages, the demo runs via curl — annoying but not catastrophic. *Mitigation:* Day 4 admin pages have explicit "minimum viable" scope in §Day 4; do not gild.
2. **Design-system drift (Days 2-4, medium likelihood, quarter-day per instance).** Wireframes are 6 weeks old; copy may have drifted. *Mitigation:* Sally does a Monday sweep and files inconsistencies before implementation starts.
3. **Playwright infrastructure setup (Day 5, medium likelihood, half-day slip).** Playwright isn't currently wired into the repo. Node.js + browser bundles + Docker compatibility. *Mitigation:* if Playwright turns out to be a rabbit hole, fall back to OBS + manual recording.
4. **Demo-mode compressed timing edge cases (Day 1, low likelihood, quarter-day slip).** `close_time = now + 3min` at seed time might drift if the operator waits before demoing. *Mitigation:* seed script prints the exact `close_time` + "run demo-close-reveal by <TIMESTAMP>".
5. **Winner-claim UX (Day 5, low likelihood, half-day slip).** If the mobile winner_notification screen is fiddly, cut to just showing the winner status without a "claim" flow. Backend accepts the claim; the demo doesn't have to demo it.

---

## 7. Cross-week dependencies

**Week 7 leaves in place for V1 hardening:**
- Admin UI: needs full RBAC role UI (V1 5-role split), draw postponement UX, entrant management.
- Mobile: needs WhatsApp integration, real KYC flow, self-exclusion enforcement UI.
- Public: needs multi-draw browsing, historical proofs archive.
- Observability: Sentry, structured logs.

**Week 7 explicitly leaves for later:**
- Load / performance testing (V1 Phase 4).
- CI hardening beyond current baseline (Phase 5).
- Managed-platform deploy (Phase 5).

---

## 8. Success gates (V0.5 demo — the actual §6 gates from v0.5-demo-plan)

- [ ] Every flagship flow step (§2, all 16) runs end-to-end without error on a clean laptop.
- [ ] `docker compose up` starts everything in < 60 seconds.
- [ ] `make demo-reset` wipes and reseeds in < 30 seconds.
- [ ] Audit-log verifier script produces same winner when re-run against published proof.
- [ ] Design pass sign-off by founder (Sally + founder walk-through).
- [ ] Founder walks demo 20+ times without a stumble.
- [ ] Fresh clone works on a second engineer's laptop in < 15 minutes.
- [ ] Screen-recording fallback exists.
- [ ] CI green on `main`.

---

## 9. Asks to founder before Day 1 code starts

Five decisions block Day 1. Recommendations below.

1. **Frontend scope — full apps or curl-driven demo?**
   Options: (a) full mobile Flutter + admin Next.js as scoped above; (b) curl for admin ops + minimal mobile browse-only; (c) hybrid — mobile hero flow + admin curl.
   **Recommendation: (a) full frontend as scoped.** V0.5 is an investor pitch. "It's a website + an app you can use" reads much stronger than "curl commands + a text output". If Day 4 slips, cut audit-log admin table first (curl-driven is acceptable for that surface).

2. **Winner claim — full mobile flow or backend-only?**
   Options: (a) mobile screen with claim button + audit event (as scoped); (b) backend endpoint only + demo the state via curl; (c) skip entirely — demo ends at "winner selected".
   **Recommendation: (a) full mobile flow.** Step 7 of the flagship flow is in the pitch; users won't buy the story if the claim isn't shown.

3. **Screen recording — Playwright script or manual OBS?**
   Options: (a) Playwright automated recording (reproducible, versioned); (b) manual OBS session (faster to produce, harder to update); (c) both.
   **Recommendation: (a) Playwright automated.** If setup takes > half a day, fall back to (b). The fallback video is a "last resort" — spending 2 days perfecting an auto-record is bad economics.

4. **Demo-mode timing — how compressed?**
   Options: (a) close_time = seed + 3min, draw_time = seed + 4min (as scoped); (b) close_time = seed + 30sec (aggressive — one-take demo); (c) close_time = seed + 10min (buffered — safer for pitches with Q&A).
   **Recommendation: (a) 3 min close + 1 min buffer.** Fits a 5-minute pitch window comfortably. Let founder override via env var.

5. **Public proof page — SSR (default) or client-rendered?**
   Options: (a) Next.js server-rendered (SEO-friendly, no JS on first paint); (b) client-rendered with a spinner; (c) static-at-build (won't work — proof is dynamic per draw).
   **Recommendation: (a) SSR.** Fits the "regulator can screenshot this without a browser dev-tools tab open" trust-story requirement. First paint is fast; hydration only for the copy-button.

Adaeze's items in §5 (public proof PII posture, trust-story copy) still owed by Day 3.

---

## 10. Cross-references

- `v0.5-demo-plan.md §5 Week 7`, §6 (V0.5 success gates), §2 (all 16 flagship flow steps).
- `week-6-build-plan.md` — foundation (draw engine, proof endpoint, verifier CLI).
- Wireframes: `02-skill-question.md`, `04-buy-ticket-skill-payment.md`, `05-my-ticket-detail.md`, `10-my-tickets.md`, `11-close-draw.md`, `12-reveal-draw.md`, `13-audit-log-admin.md`, `14-public-proof-page.md`, `15-how-it-works.md`, `16-responsible-play.md`.

---

💻 *End of Week 7 build plan. Awaiting sign-off on §9 (5 asks) to start Day 1 Monday 2026-08-11.*

# Week 4 Build Plan — Wallet & Ledger + Payment (Paystack sandbox)

**Drafted:** 2026-07-14 (Week 3 close; Week 4 kickoff on founder sign-off)
**Drafted by:** 💻 Amelia (BMad Dev)
**Status:** **Approved 2026-07-15** — founder resolved all §9 asks; ready to start Day 1 Monday.
**Applies to:** V0.5 investor demo; Wallet + Payment slices of the flagship flow.
**Pairs with:** `v0.5-demo-plan.md §5 Week 4`, `week-3-build-plan.md` (foundation), `docs/adr/ADR-{002,003,004,008}.md`, `_bmad-output/planning-artifacts/design/wireframes/{04,09,10,13}.md`.

---

## 0. Founder decisions (2026-07-15)

Resolves §9 asks. Applied throughout the plan below.

| # | Ask | Decision | Impact |
|---|---|---|---|
| 1 | Paystack sandbox credentials | **Stub Paystack entirely for Week 4** | No real HTTP calls to Paystack; Day 3 adapter runs against captured fixture responses (`backend/tests/payment/fixtures/paystack/*.json`). Day 4 webhook exercises the real HMAC-SHA-512 path against a locally-generated signature using a test webhook secret. Real credentials + live sandbox round-trip land Week 5 when the mobile ticket-purchase UI needs a real checkout URL — deferred as a Week 5 blocking prereq for founder. |
| 2 | Fee-handling shape | **Trust Paystack's response `fees` field** | Fee amount comes from the vendor response payload, not a hardcoded schedule. Fixture files include representative `fees` values (₦100 flat below ₦2,500; 1.5% + ₦100 above; capped at ₦2,000). Adapter surfaces the fee on `PaymentResult`; `record_deposit` posts it as a separate ledger entry per ADR-008 §Fee handling. |
| 3 | Outbox pattern (ADR-002) | **Direct call in Week 4; outbox refactor Week 6+** | Paystack webhook handler calls `wallet.service.record_deposit` synchronously in the same DB transaction. Documented debt in commit + `docs/adr/ADR-002-outbox-pattern-for-async-work.md` (Amelia adds an Amendment section noting the V0.5 deferral). Full outbox lands Week 6 with the draw-engine module which genuinely needs async fan-out. |
| 4 | `WALLET_ALLOW_STUB_DRAW` flag | **Yes, flag + stub** | Week 4 posts ticket-purchase transactions to a placeholder `prize_pool` account keyed on a string `draw_id`. Flag default `true` in `atlas.config` under `ATLAS_WALLET_ALLOW_STUB_DRAW`; must be `false` in prod. Startup check refuses to boot with flag `true` when `ATLAS_ENV=production`. Week 5 flips the flag off as ticket module lands and real draws exist. |
| 5 | Idempotency-key retry semantics | **ADR-004 verbatim** | Same key + same body → return cached response verbatim; same key + different body → 409 Conflict. Matches identity module + ADR-004 §Processing step 2. No payment-specific override. |

Adaeze's items in §5 (audit-payload redaction, fee-split accounting posture) still owed by Day 4.

---

## 1. Scope

**In.**
- Migration 0004: `ledger_accounts`, `ledger_entries`, chart-of-accounts seed for the 6 V1 account types, transaction-balance trigger (`DEFERRABLE INITIALLY DEFERRED`), append-only enforcement (revoke UPDATE/DELETE), unique idempotency index.
- `atlas.wallet.ledger` primitive: `post_transaction(entries: list[LedgerEntryDraft], idempotency_key)` — the sole entry point for writing to `ledger_entries`. Grep-enforced.
- `atlas.wallet.service` domain helpers: `record_deposit`, `record_ticket_purchase` (stub until ticket module lands Week 5), `record_prize_award`, `record_refund`. Each produces balanced transactions.
- `atlas.wallet.queries.balance_of(account_id)` — the SUM(direction*amount) query.
- Migration 0005: `payment_intents` table (state machine: initiated → pending → succeeded/failed/refunded).
- `atlas.payment.providers.protocol` per ADR-008.
- `atlas.payment.providers.paystack` — Paystack sandbox adapter implementing the protocol.
- `POST /api/v1/payments/intents` (idempotency-key required per ADR-004 §Scope).
- `POST /api/v1/payments/webhooks/paystack` — signature verification, event dispatch, wallet credit + fee posting per ADR-008 §Fee handling.
- Reconciliation-job **skeleton** (`atlas.payment.jobs.reconcile`) — signature only; nightly cron wiring is a Week 6 job.
- Integration tests: real Postgres, no mocks for the trigger + balance queries; Paystack calls stubbed at the HTTP boundary with the vendor's documented test-mode responses.

**Out** (V0.5 stubs / deferred):
- Bonus / cashback / promo accounts (ADR-003 §Alternatives — V2).
- Outbox event bus (ADR-002 full wiring) — Week 4 uses direct in-transaction wallet crediting from the webhook handler; outbox refactor is a documented Week 6+ debt.
- Reconciliation cron (Week 6).
- Withdrawals (V1).
- Refund UX (Week 5 minimum; V1 hardening).
- Multi-currency (V1).
- Fraud rules / velocity checks (V1).

---

## 2. Day-by-day breakdown

Each day ends demoable to founder over Zoom in < 3 minutes.

### Day 1 (Mon 2026-07-21) — Ledger schema + primitives

- `backend/migrations/versions/0004_ledger.py` — ledger_accounts + ledger_entries per ADR-003 §Schema exactly; append-only grants; unique idempotency index; **deferred-constraint trigger** that at COMMIT checks `SUM(direction*amount) = 0` per `transaction_id`.
- Seed chart of accounts: 4 operator-level rows (`operator_revenue`, `refund_payable`, `payment_gateway_clearing` for paystack, `tax_payable`) in the same migration. `user_wallet` and `prize_pool` rows are created lazily by the service on first-use (per user / per draw).
- `backend/src/atlas/wallet/models.py` — LedgerAccount, LedgerEntry ORMs.
- `backend/src/atlas/wallet/ledger.py` — `LedgerEntryDraft` dataclass + `async def post_transaction(session, *, entries, idempotency_key, external_ref) -> uuid.UUID` returning the transaction_id. Balance validation happens in the trigger; the primitive is the sole INSERT path.
- `backend/src/atlas/wallet/queries.py` — `balance_of(session, *, account_id) -> int` (kobo).
- CI grep: any INSERT into `ledger_entries` outside `atlas/wallet/ledger.py` fails the build. Any migration adding a `balance` column to a users-or-accounts table fails the build (ADR-003 §Invariants 1).
- Tests:
  - `tests/unit/test_ledger_math.py` — draft balancing helper, direction sign semantics.
  - `tests/wallet/test_ledger_trigger.py` — unbalanced INSERTs raise on COMMIT; balanced ones commit; contra-entries balance a prior transaction.

**Demoable EOD:** `docker compose run --rm backend pytest -q tests/wallet` → green; `SELECT * FROM ledger_accounts` shows the 4 operator seed rows.

### Day 2 (Tue) — Wallet service helpers + audit hookup

- `atlas.wallet.service`:
  - `get_or_create_user_wallet(session, user_id) -> LedgerAccount`
  - `record_deposit(session, *, user_id, amount_minor, external_ref, idempotency_key)` → debits `payment_gateway_clearing`, credits `user_wallet`. Emits `wallet.deposit_credited` audit event.
  - `record_ticket_purchase(session, *, user_id, draw_id, amount_minor, idempotency_key)` — draws don't exist yet, so the debit side goes to `operator_revenue` and credit-side to a *placeholder* `prize_pool` account keyed on `draw_id` string (Week 5 ticket module wires the real draw). Emits `wallet.ticket_purchase_posted` audit event. Behind a feature flag `WALLET_ALLOW_STUB_DRAW` (default true in V0.5).
  - `record_prize_award(session, *, user_id, draw_id, amount_minor, idempotency_key)` → debits `prize_pool`, credits `user_wallet`. Emits `wallet.prize_awarded`.
  - `record_refund(session, *, user_id, amount_minor, reason, idempotency_key)` → debits `refund_payable`, credits `user_wallet`. Emits `wallet.refund_issued`.
- Audit events land through `atlas.audit_log.writer.append(...)` — same discipline as identity module.
- Tests:
  - Happy path per helper: transaction balances; balance_of returns expected values.
  - Idempotency: replay same key → no duplicate entries, transaction_id returned matches original.
  - Concurrent posting (two parallel calls with different keys) → both land, chain unaffected.

**Demoable EOD:** shell script that runs 3 deposits, 2 ticket purchases, 1 prize award on a demo user; final `balance_of(user_wallet) == expected`, audit-log chain intact.

### Day 3 (Wed) — Payment intents + Paystack adapter (stubbed per §0.1)

- `backend/migrations/versions/0005_payment_intents.py` — `payment_intents` (id, user_id, amount_minor, currency, method, status, vendor_reference, checkout_url, idempotency_key UNIQUE, metadata, created_at, updated_at). State enum per ADR-008.
- `atlas.payment.providers.protocol.py` per ADR-008 §Protocol surface — `PaymentProvider` protocol + `PaymentIntent` / `PaymentResult` / `WebhookEvent` dataclasses + enums.
- `atlas.payment.providers.paystack.py` — implements the protocol. Real HTTP surface **wired but disabled** (`ATLAS_PAYSTACK_STUB_MODE=true` in V0.5 default; adapter short-circuits to fixture responses). Real HTTP-call code path exercised only by contract tests using `pytest-httpx` mocks — no live sandbox round-trip in Week 4 per §0.1.
- `atlas.payment.providers.paystack_fixtures.py` — deterministic fixture responses for `initialize`, `charge.success`, `charge.failed` derived from Paystack's published example payloads. Fixture `checkout_url` is `http://mock-paystack.local/checkout/{ref}` so callers see it's a stub.
- `atlas.payment.service`:
  - `create_intent(session, *, user_id, amount_minor, method, description, idempotency_key)` — persists the `payment_intents` row, calls provider (returns fixture response in stub mode), updates row with `vendor_reference` + `checkout_url`, emits `payment.intent_created` audit event.
- `atlas.payment.routes`:
  - `POST /api/v1/payments/intents` — Idempotency-Key required. Returns `{payment_intent_id, checkout_url, expires_at}`.
- `atlas.config` gets `paystack_secret_key: SecretStr | None` (optional in stub mode), `paystack_public_key: str | None`, `paystack_webhook_secret: SecretStr` (required — the HMAC path exercises this even in stub mode via signed test webhooks), `paystack_stub_mode: bool` (default true in V0.5).
- Tests:
  - `tests/payment/test_paystack_adapter.py` — stub-mode path returns fixture; live-mode path (with mocked HTTP via `pytest-httpx`) verifies request shape (auth header, JSON body) and response parsing.
  - `tests/payment/test_intent_endpoint.py` — creates intent → 201 with expected shape; idempotent replay returns cached response.

**Demoable EOD:** `curl -X POST http://localhost:8000/api/v1/payments/intents -H 'Idempotency-Key: {uuid}' -H 'Authorization: Bearer {session}' -d '{"amount_minor": 500000, "method": "card"}'` returns 201 with a mock `checkout_url` (real sandbox URL comes Week 5 when founder provisions the sandbox account).

### Day 4 (Thu) — Paystack webhook + wallet credit

- `atlas.payment.providers.paystack.verify_webhook(raw_body, headers)` — HMAC-SHA-512 signature check against `x-paystack-signature` per Paystack docs. Returns `WebhookEvent` on pass, raises `InvalidSignature` on fail.
- `atlas.payment.routes.paystack_webhook`:
  - `POST /api/v1/payments/webhooks/paystack` — reads raw body BEFORE parsing (Starlette `request.body()`), calls `verify_webhook`, dispatches on event type:
    - `charge.success` → look up payment_intent by vendor_reference, mark succeeded, call `wallet.service.record_deposit(...)`, post the Paystack fee as a separate transaction per ADR-008 §Fee handling (debit `operator_revenue` + credit `payment_gateway_clearing` for the fee).
    - `charge.failed` → mark failed, emit `payment.failed` audit.
  - Handler is idempotent by `vendor_reference` — receiving the same webhook twice is a no-op (checked via ledger_entries.idempotency_key uniqueness).
  - Signature-fail returns 401 with NO body parsing (ADR-008 §Invariants 2).
- Tests:
  - Valid signature + `charge.success` webhook → payment_intent succeeded, user_wallet credited, fee entry posted, both audit events chained.
  - Same webhook replayed → no duplicate ledger entries.
  - Bad signature → 401, no state change.
  - `charge.failed` webhook → payment_intent failed, no ledger entries.
- Recon skeleton: `atlas.payment.jobs.reconcile.py` — stub with `TODO(week-6)` markers around the fetch call; unit test the diffing helper (given fake settlement report + ledger sum, computes diff).

**Demoable EOD:** feed a signed test webhook body via `curl` (signed with the local `ATLAS_PAYSTACK_WEBHOOK_SECRET` using a small helper script `infrastructure/scripts/sign_paystack_webhook.py`) → observe `SELECT balance_of(user_wallet)` increase by the deposited amount, with the fee visible as a separate entry.

### Day 5 (Fri) — E2E flow + hardening

- E2E integration test: register → login → create payment intent → simulate Paystack webhook → assert wallet balance updated → assert audit-log chain intact across all events (register + otps + password_set + session_created + payment_intent_created + payment_confirmed + wallet_deposit_credited).
- CI grep additions:
  - No direct Paystack SDK imports outside `atlas.payment.providers.paystack` (ADR-008 §Invariants 1).
  - No `.get_secret_value()` reads outside `atlas.config` and `atlas.payment.providers.paystack` (Paystack adapter needs the key for the outbound call).
- Runbook stub: `docs/runbooks/paystack-webhook-outage.md` — 3 pages: symptom, immediate mitigation, root-cause checklist.
- Fresh-clone drill v2 with the wallet+payment path included. Target still < 15 min; hard 20 min.
- Week 4 exit gates verified (§9 below).

**Demoable EOW:** `git clone && make setup && make dev && make bootstrap` → register a test user via curl → create intent → simulate webhook → wallet shows the deposit → audit-log chain green from register through deposit.

---

## 3. Module contracts

### 3.1 Wallet endpoints (internal — no HTTP surface Week 4)

Wallet is called only by other backend modules (payment webhook, later: ticket module). No `POST /api/v1/wallet/*` routes this week. Balance is exposed via `GET /api/v1/users/me/wallet` **in Week 5** when the mobile home screen needs it.

### 3.2 Payment endpoints (Week 4)

| Method | Path | Idempotency | Purpose |
|---|---|---|---|
| `POST` | `/api/v1/payments/intents` | required | Create a payment intent → returns Paystack checkout URL. |
| `POST` | `/api/v1/payments/webhooks/paystack` | n/a — signature-gated | Paystack event ingest. |
| `GET`  | `/api/v1/payments/intents/{id}` | n/a | Read current state of an intent (used by Flutter to poll if webhook is delayed). |

### 3.3 Chart of accounts (Day 1 seed)

| Type | Owner type | Owner id | Notes |
|---|---|---|---|
| `operator_revenue` | operator | NULL | Singleton |
| `refund_payable` | operator | NULL | Singleton |
| `payment_gateway_clearing` | gateway | `paystack` | One per gateway; V1 has 1 |
| `tax_payable` | operator | NULL | Singleton, unused Week 4 |

`user_wallet` and `prize_pool` are lazily created on first-use.

### 3.4 Module boundary invariants (extend §4.4 of Week 3 plan)

- No INSERT/UPDATE/DELETE on `ledger_entries` outside `atlas.wallet.ledger`. CI grep.
- No `ledger_accounts.balance`-style mutable column anywhere. CI grep on migrations.
- No direct import of `paystack` (or `paystackapi` etc.) outside `atlas.payment.providers.paystack`. CI grep.
- Payment webhook endpoint reads raw body BEFORE any JSON parsing; signature verification precedes trust.

---

## 4. Test strategy (for Murat 🧪)

Real Postgres for the trigger + balance math (real database behaviour is the point). Paystack HTTP calls stubbed at the wire (`pytest-httpx` — I'll add the dep Day 3). Real webhook signatures generated in tests using a test webhook secret so verify_webhook exercises the real HMAC path.

**Unit** (`backend/tests/unit/`):
- Ledger-entry balancing math (given N entries, verify sum-of-direction-times-amount).
- Paystack fee computation (given gross amount + fee schedule, verify fee minor amount).
- Webhook HMAC round-trip.

**Integration** (`backend/tests/wallet/`, `backend/tests/payment/`):
- All the Day 2 + Day 4 scenarios above.
- Chain integrity across the full flow (§ Day 5 E2E).

**Contract** (`backend/tests/contract/`):
- OpenAPI stub validates `POST /payments/intents` and the webhook shape.

**Not in Week 4:**
- E2E via Playwright.
- Load / performance.
- Paystack live-mode round-trip (V1).

Murat gets a stub at `_bmad-output/test-artifacts/test-design/week-4-wallet-payment.md` for expansion.

---

## 5. Handoffs and dependencies

### To 🛡️ Tobi (DevSecOps)
- **Day 3 blocking:** review the Paystack secret provisioning approach. Confirm `.env.example` name + docker-compose passthrough shape matches ADR-012 discipline.
- **Day 4 blocking:** confirm the webhook endpoint is safe to expose publicly (rate-limit at the ingress? behind a signed URL?). V0.5 answer likely "expose on localhost only until Phase 5"; confirm.
- **Day 5 non-blocking:** first pass at `docs/runbooks/paystack-webhook-outage.md`.

### To 🏗️ Winston (Architect)
- **Day 1 blocking (small):** confirm the deferred-constraint trigger approach vs. a savepoint-based check. Recommend deferred trigger (simpler, standard Postgres pattern).
- **Day 3 blocking:** sign off on the Paystack adapter's `raw_response_redacted` field list. Any field with card/PAN/CVV/authorization-code touched must NOT persist.
- **Day 4 blocking:** confirm outbox deferral (direct-call-from-webhook is Week 4; full ADR-002 outbox is Week 6+).

### To 🎨 Sally (UX)
- Expected zero. Wallet has no UI Week 4 (Week 5 adds the mobile home wallet-balance chip). Payment webhook is server-side only.

### To ⚖️ Adaeze (Compliance & Risk)
- **Day 2 non-blocking:** wallet audit-event payloads — what redaction is required? Recommend `{user_id, amount_minor, transaction_id}` and no email/PAN/phone in wallet events (they exist on user rows). Confirm.
- **Day 3 non-blocking:** payment audit-event payloads — same question for `payment.intent_created`. Recommend `{user_id, amount_minor, vendor_reference, method}` — no card details ever.
- **Day 4 blocking-ish (by Fri):** confirm the fee split (deposit gross → user, fee → operator_revenue) matches the accounting posture legal will want to see.

---

## 6. Risks

Ranked by likelihood × slip-impact.

1. **Paystack sandbox account provisioning (Day 3, high likelihood, half-day slip).** Founder must create a test-mode Paystack account + share the test secret/public/webhook secret. If this drags past Day 3 morning, Day 3 slips or Amelia stubs Paystack entirely and swaps in real creds Day 4. *Mitigation:* founder does this Fri afternoon Week 3 (before Week 4 starts).
2. **Deferred-constraint trigger + connection-pool interaction (Day 1, medium likelihood, half-day slip).** SQLAlchemy async connection reuse might commit before the deferred trigger fires as expected. *Mitigation:* explicit `DEFERRABLE INITIALLY DEFERRED` on the constraint, plus an integration test that opens two connections and posts unbalanced entries to confirm rejection.
3. **Webhook signature edge cases (Day 4, medium likelihood, quarter-day slip).** Paystack's `x-paystack-signature` docs are precise but different from Stripe's — HMAC-SHA-512 hex over raw body with the webhook secret. *Mitigation:* write the HMAC unit test first (Day 4 morning) with a captured production webhook body from Paystack's docs before wiring the handler.
4. **Idempotency-key collision across payment intent + ledger entry (Day 4, low likelihood, quarter-day slip).** The `Idempotency-Key` from the client applies to the payment-intents row; the ledger_entries idempotency_key must be derived (e.g. `f"deposit:{vendor_reference}"`) so wallet credits are independently idempotent even if the client key is missing on the webhook path. *Mitigation:* explicit test for double-webhook delivery.
5. **Kobo rounding drift (Day 4, low likelihood, half-day slip if caught in prod).** Paystack returns integer kobo already; we store integer kobo; no float involved. Confirm via a golden-vector unit test on Paystack's example response body. *Mitigation:* type discipline (`int` everywhere for `amount_minor`; ruff rule if `float` appears in wallet/payment).
6. **Two-approval PR gate slowing merges (Day 3-5, high likelihood, no critical-path slip).** Every ledger + payment PR needs EL + Finance approval per ADR-003 / ADR-008. Founder wears both hats — expected friction, not a fix.

Not a Week 4 risk but a Week 5 blocker: Ticket module depends on wallet.record_ticket_purchase using a real `draw_id`. Week 5 Day 1 needs the draw skeleton before the ticket calls fire.

---

## 7. Cross-week dependencies

**Week 4 leaves in place for Week 5:**
- `atlas.wallet.service.record_ticket_purchase` — Week 5 replaces the stub `draw_id` with the real draw.
- `atlas.wallet.queries.balance_of` — Week 5's `GET /api/v1/users/me/wallet` uses it.
- Paystack payment intent creation — Week 5 mobile ticket-purchase UI kicks off the intent.
- Webhook wallet credit — Week 5 mobile UI polls `GET /payments/intents/{id}` to know when to enable "buy tickets".

**Week 4 explicitly leaves for later:**
- Withdrawals (V1).
- Refund UX (Week 5 minimum via admin; V1 for self-serve).
- Full ADR-002 outbox (Week 6+).
- Reconciliation cron (Week 6).
- Multi-currency (V1).

---

## 8. Success gates (Week 4 exit criteria — for founder sign-off Fri EOD)

- [ ] Migration 0004+0005 land clean; `alembic upgrade head` from empty DB succeeds.
- [ ] Deferred trigger rejects an unbalanced transaction (integration test proves it).
- [ ] `atlas.wallet.ledger.post_transaction` is the ONLY writer to `ledger_entries` (CI grep green).
- [ ] `POST /api/v1/payments/intents` returns a real Paystack sandbox `checkout_url`.
- [ ] Feeding a signed test webhook credits the user wallet and posts the fee entry — SQL query verifies.
- [ ] Chain-integrity SQL passes across the register→deposit flow (all events chain to prior).
- [ ] `docs/runbooks/paystack-webhook-outage.md` exists in Draft.
- [ ] CI green on PR (backend, admin, mobile, module-boundaries).
- [ ] `docs/AI-INTEGRATION-LOG.md` has entries for Week 4 Days 1-5.

---

## 9. Asks to founder before Day 1 code starts

**All 5 resolved 2026-07-15 — see §0.** Preserved below as historical record.

1. **Paystack sandbox credentials.** → **Stub Paystack entirely for Week 4.** Real credentials + live sandbox round-trip deferred to Week 5 as a blocking prereq for founder.
2. **Fee handling shape.** → **Trust Paystack's response `fees` field.**
3. **Outbox pattern deferral.** → **Direct call in Week 4; ADR-002 outbox refactor Week 6+.**
4. **`WALLET_ALLOW_STUB_DRAW` flag.** → **Yes, flag + stub.** Startup check refuses `true` in production.
5. **Idempotency-key semantics on payment retry.** → **ADR-004 verbatim.**

Adaeze's items in §5 (wallet + payment audit payload redaction, fee-split accounting posture) still owed by Day 4.

---

## 10. Cross-references

- `v0.5-demo-plan.md §5 Week 4`, §6 (success gates).
- `week-3-build-plan.md` — the foundation this plan extends (identity, audit_log writer, idempotency middleware, config discipline).
- `docs/adr/ADR-002` (outbox — deferred), `ADR-003` (ledger schema + invariants), `ADR-004` (idempotency), `ADR-008` (payment adapter + webhook).
- Wireframes touched (later weeks): `04-buy-ticket-skill-payment.md`, `13-audit-log-admin.md`.

---

💻 *End of Week 4 build plan. Awaiting sign-off on §9 (5 asks) to start Day 1 Monday 2026-07-21.*

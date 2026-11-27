# ADR-010 Self-Exclusion — Implementation Plan

**Drafted:** 2026-11-24
**Drafted by:** 🏗️ Winston (bmad-agent-architect), at ⚖️ Adaeze's request (REVIEW-002 §6, §7 item 3)
**Implementer:** 💻 Amelia
**Mandatory reviewers:** ⚖️ Adaeze (Identity is compliance-sensitive, `AINE-AGENTS.md §3`), 🧪 Murat
**Approver:** S1408661 (Engineering Lead)
**Status:** Proposed. **Phase A is buildable now. Phase B is blocked.**

---

## 1. The finding that shapes everything below

**ADR-010 cannot be implemented as written.** Its primary enforcement point does not exist and cannot be built in this sprint.

ADR-010 §Enforcement points names three. Assessed against the codebase on 2026-11-24:

| # | Enforcement point per ADR-010 | Buildable? |
|---|---|---|
| 1 | **At KYC submission** — hash the BVN, look it up before any vendor call | ❌ **No.** There is no KYC module. `backend/src/atlas/` has no `kyc` package and no `kyc` symbol anywhere. ADR-007 was approved and never built |
| 2 | **At account creation (pre-KYC)** — allow registration, mark `pending_kyc`, block at KYC | ❌ **No.** Explicitly delegates the block to point 1. Also: `users.status` has no `pending_kyc` value — the CHECK permits only `pending_verification`, `active`, `closed` |
| 3 | **At login** — revoke sessions, refuse future logins | ✅ **Yes**, and mostly already there (§3.1) |

BVN is collected **nowhere**. The only trace in the codebase is `config.py:145` — `bvn_pepper: SecretStr | None = None`. A pepper with nothing to hash.

**So the BVN-keyed registry — the entire mechanism ADR-010 exists to specify — is downstream of ADR-007.** Plan accordingly rather than pretending otherwise: Phase A delivers real self-exclusion without BVN; Phase B adds the cross-account guarantee when KYC lands.

**What Phase A does and does not buy, stated precisely, because the copy depends on it:**

- ✅ A user who asks to stop **is stopped**. Account closed, sessions killed, no further entry possible.
- ❌ That user **can still register again** with a different email and phone. Only BVN closes that door, and BVN needs KYC.

Adaeze: the responsible-play page can truthfully say *"you can permanently close your account"* after Phase A. It **cannot** say *"a fresh account with the same details cannot bypass it"* until Phase B. That sentence was the false claim found in REVIEW-002 §6.1 and it must not return early.

---

## 2. What already exists (Phase A is cheaper than it looks)

Scaffolding found in place, all free:

- **`users.status` already permits `'closed'`** (`identity/models.py:32`). The value is reserved and **nothing in the codebase ever sets it.**
- **Login already refuses a non-active user** — `session_service.py:85`: `if user.status != "active"`. Setting status to `'closed'` satisfies ADR-010 enforcement point 3 with **no new login code.**
- **`session_service.revoke_current`** exists. Needs a `revoke_all_for_user` sibling.
- **`wallet.record_refund`** exists (`wallet/service.py:416`) — ledger-side refund posting is real.
- **`login_mfa`** is already a valid OTP purpose (`identity/models.py:67`), so the ADR's MFA-challenge requirement has a delivery channel.
- Audit writer, idempotency guard, and RBAC are all in place.

---

## 3. Phase A — account-level self-exclusion

**Estimate: 2–3 days.** Entirely within Identity + Ticket.

### 3.1 Data

New table `self_exclusions`, keyed on `user_id`, with the BVN column present-but-nullable from day one so Phase B is a backfill rather than a migration of a live table:

```sql
CREATE TABLE self_exclusions (
  user_id        UUID PRIMARY KEY REFERENCES users(id),
  bvn_hash       TEXT UNIQUE,          -- NULL until ADR-007 lands (Phase B)
  excluded_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  excluded_by    TEXT NOT NULL,        -- 'user_self' | 'operator' | 'regulator'
  excluded_by_id UUID REFERENCES users(id),
  reason         TEXT,
  notes          TEXT,
  CONSTRAINT excluded_by_enum CHECK (excluded_by IN ('user_self','operator','regulator'))
);
CREATE INDEX idx_self_exclusions_bvn_hash ON self_exclusions(bvn_hash) WHERE bvn_hash IS NOT NULL;
```

**Deviation from ADR-010:** the ADR specifies `bvn_hash TEXT PRIMARY KEY`. Phase A has no BVN, so the primary key is `user_id` and `bvn_hash` is a nullable unique column. Phase B populates it. **This needs an ADR-010 amendment — see §6.**

### 3.2 Service — `atlas.identity.self_exclusion`

Sole writer to `self_exclusions`. One transaction:

1. Insert the exclusion row.
2. `users.status = 'closed'`.
3. Revoke every session for the user (`revoke_all_for_user`, new).
4. Audit `self_exclusion.activated`.

Idempotent on `user_id` — a replay returns the existing row, no second audit entry. Add `self_exclusion.activated` to the ADR-002 outbox allowlist (deferred: no consumer yet).

### 3.3 Enforcement — **the purchase-path gap is the important one**

| Point | Work |
|---|---|
| **Login** | **None.** `session_service.py:85` already blocks. Soften the error copy to "this account has been closed" per ADR-010 |
| **Purchase** | **NEW — and this is the real hole.** `ticket/routes.py::purchase` validates draw state and entitlement only; it never looks at `users.status`. A closed user holding a live session could buy until it expires. Sessions are revoked at exclusion, so the window is narrow — but "narrow" is not an enforcement story. Add an explicit check in `issue_paid`, server-side, not just at the route |
| **Skill question** | Add the same check to `next_question` — cheap, and stops a closed user starting a flow that will fail at the end |
| **KYC** | Phase B |

**Invariant for Murat:** a closed user cannot obtain a ticket by any path. Test it at the service layer, not just through the route — the route is one caller and `issue_paid` is reachable from the webhook.

### 3.4 Wallet balance — deliberately NOT refunded in Phase A

ADR-010 §User-facing flow requires any balance be refunded to the originating payment method, with escheatment if refund is impossible.

**Neither exists.** `payment/service.py:189` says outright: *"refunded before we've implemented refunds"* — there is no Paystack refund call. And `docs/compliance/escheatment-policy.md`, which ADR-010 cites as Phase 0 work, was never written.

Phase A therefore **holds the balance** on the closed account and surfaces it to support, rather than silently doing nothing while the ADR claims a refund happens. In V0.5 the wallet is winnings-only and ticket purchase is direct-to-Paystack, so a non-zero balance at exclusion is rare — but rare is not never, and a user who self-excludes with money in the account must not simply lose it.

**Adaeze — two asks:** (a) is holding acceptable for Phase A, or does this block? (b) the escheatment policy is yours and is a Phase B dependency regardless.

### 3.5 Surfaces

- `POST /api/v1/users/me/self-exclude` — auth + Idempotency-Key. Body requires the literal string `EXCLUDE` plus a valid `login_mfa` OTP, per ADR-010's confirmation requirements.
- Mobile: *Settings → Account → Close my account*, with the irreversibility interstitial. Replaces the `home_screen.dart:246` placeholder.
- Admin: read-only exclusion list for support. **No un-exclude control** — V1 has no reversal, so the UI must not imply one.
- Copy: Adaeze drafts, per the `AINE-AGENTS.md §6` gate. Must state the Phase A limit plainly (§1).

---

## 4. Phase B — BVN-keyed cross-account enforcement

**BLOCKED on ADR-007 (KYC vendor adapter). Do not start.**

When KYC lands: hash BVN with the `bvn_pepper` already in config, backfill `bvn_hash`, add the pre-vendor lookup with `self_exclusion.match` audit, and only then may the stronger copy return.

Carry forward from ADR-010 as hard invariants: BVN never stored in plaintext (CI fixture test); exclusion lookup precedes every KYC vendor call (adapter unit test); **the pepper is never rotated** — rotation invalidates the whole registry.

---

## 5. Sequencing

| | Work | Depends on | Est. |
|---|---|---|---|
| A1 | Migration + ORM + `revoke_all_for_user` | — | 0.5d |
| A2 | `self_exclusion` service + audit + outbox allowlist | A1 | 0.5d |
| A3 | Purchase + skill-question enforcement, service-layer tests | A2 | 0.5d |
| A4 | Route + OTP challenge + idempotency | A2 | 0.5d |
| A5 | Mobile settings flow | A4 | 0.5d |
| A6 | Admin read-only list | A4 | 0.25d |
| A7 | Copy (Adaeze) + responsible-play page update | A1–A6 | — |
| B | BVN registry | **ADR-007** | blocked |

---

## 6. ADR-010 amendment required before merge

Per CLAUDE.md, ADR changes go through me, not retroactive edits. Phase A deviates in four ways:

1. **Primary key** `bvn_hash` → `user_id`, with `bvn_hash` nullable (§3.1).
2. **New enforcement points** at ticket purchase and skill-question issue. The ADR names only KYC, registration and login — and the purchase gap (§3.3) is a genuine defect in the ADR, not just in the code.
3. **Wallet refund deferred** — the ADR's user-facing flow is unbuildable without payment refunds and an escheatment policy (§3.4).
4. **Two-phase delivery**, where the ADR assumes a single KYC-gated mechanism.

I'll draft the amendment alongside A1 so the spec lands before the code — `delivery-framework.md §12`, and a correction of the sequencing failure recorded in AMEND-001 §0.

---

## 7. What this does not fix

Phase A makes the responsible-play page honest about self-exclusion. It does nothing for the other two gaps Adaeze raised: **no per-user entry cap and no spend ceiling**, now sitting alongside unlimited entries. Those are a separate decision for the founder, not an ADR-010 deliverable — but a responsible-play posture built on exclusion alone, with no limits of any kind in front of it, is a thin one.

— 🏗️ Winston

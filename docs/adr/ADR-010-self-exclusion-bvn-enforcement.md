# ADR-010: Self-exclusion enforced via BVN-keyed registry

**Status:** Approved
**Date:** 2026-06-29
**Approved by:** S1408661 (Engineering Lead + Compliance Lead, sole founder) on 2026-07-02
**Reversibility:** One-way door once production users exist.

## Context

`PRD.md §3.2` requires that a user can self-exclude permanently from settings, and that **re-registration with the same BVN is blocked**. Self-exclusion is the V1's primary responsible-gaming control. Email and phone numbers can be changed; BVN cannot. Using BVN as the exclusion key prevents trivial circumvention.

This ADR commits the mechanism.

## Decision

### Registry

```sql
CREATE TABLE self_exclusions (
  bvn_hash       TEXT PRIMARY KEY,     -- HMAC-SHA-256(pepper, BVN) — pepper in secret manager
  excluded_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  excluded_by    TEXT NOT NULL,         -- "user_self" | "operator" | "regulator"
  excluded_by_id UUID,                  -- operator user_id when applicable
  reason         TEXT,
  notes          TEXT
);
```

**No reversal mechanism in V1.** Self-exclusion is permanent. A V2 amendment may introduce a cool-off window and a vetted reversal process per Nigerian regulatory practice, when applicable.

### BVN hashing

- BVNs are never stored in plaintext in the application database.
- The hashing key (pepper) lives in the platform secret manager (ADR-012), accessible only to the worker and API processes.
- Hash: `HMAC-SHA-256(key=pepper, msg=normalized_bvn)`. `normalized_bvn` is the digits-only representation, no whitespace.
- The pepper is **not** rotated post-launch — rotating would invalidate the entire exclusion registry. This is documented as a known operational constraint in the Compliance runbook.

### Enforcement points

1. **At KYC submission** (per ADR-007): the BVN is hashed and looked up before any vendor call. Match → KYC returns `REJECTED` with reason `self_excluded`; no vendor call is made; the rejected attempt is audit-logged (`self_exclusion.match` event).
2. **At account creation** (pre-KYC): if a user attempts to register a phone number or email that was previously associated with an excluded user, registration is allowed *but* the account is marked `pending_kyc` and the BVN check at KYC time will block. This is intentional — we don't reveal exclusion to a re-attempting user via the registration flow; the block happens at KYC where it's expected.
3. **At login** (existing account): if an account's owning user later self-excludes, all active sessions are revoked and future logins return a polite "this account has been closed" message.

### User-facing flow

- Setting: `Settings → Account → Close my account → Self-exclude permanently`.
- Confirmation requires: typing the word `EXCLUDE`, MFA challenge, and a final "this cannot be reversed" interstitial.
- Post-exclusion: any wallet balance is refunded to the originating payment method via the Payment module; if refund is impossible (e.g. > 90 days post-deposit), the balance is escheated to a Compliance-owned account per `docs/compliance/escheatment-policy.md` (drafted in Phase 0).

### Audit

- `self_exclusion.activated` event in audit log on every exclusion.
- `self_exclusion.match` event on every KYC block.
- Compliance & Risk Agent reviews exclusion activity monthly.

## Alternatives considered

- **Phone-number or email-based exclusion only.** Lost: trivially circumvented. BVN is the only durable identifier in the Nigerian context for an adult user.
- **Storing BVN in plaintext with strong encryption at rest.** Lost: the hash is sufficient for lookup; plaintext storage of an unrecoverable national identifier is an unnecessary risk. We only need to verify presence, not retrieve.
- **Reversible exclusion with a 6-month cool-off.** Considered. Lost for V1: introduces UX, support, and compliance complexity. V1 stance is permanent; V2 re-evaluates when we have evidence about user need.
- **Outsourcing exclusion to a third-party registry** (analogous to UK's GAMSTOP). Considered. No mature equivalent exists in Nigeria today. Compliance & Risk Agent monitors for one emerging; if it ships, V2 ADR amendment to integrate.

## Consequences

**Positive:**
- Re-registration circumvention requires identity fraud (different BVN), which is itself a criminal act with high friction.
- Plaintext BVN is never stored, reducing breach impact.
- The single lookup point (KYC submission) keeps enforcement simple.

**Negative:**
- Permanent exclusion is a strong stance; some users will regret it. Accepted because the alternative (reversal flow) is more harmful in the responsible-gaming literature.
- The pepper is a single point of failure: if lost, exclusions cannot be verified. Mitigated by storing the pepper in the platform secret manager with key-vault backups per DevSecOps runbook.
- The escheatment of un-refundable balances requires a clear policy; if unclear, support gets stuck. Policy in `docs/compliance/escheatment-policy.md`, drafted Phase 0.

**Invariants:**
- BVN is never written to the application DB in plaintext. CI test against fixtures.
- Self-exclusion lookup happens before every KYC vendor call. Enforced by adapter unit test.
- The pepper is never logged, never appears in code, never appears in CI artefacts. CI secret-scanning enforces.

---

## Amendment (2026-11-24) — two-phase delivery; BVN enforcement is blocked on ADR-007

**Proposed by:** 🏗️ Winston · **Requested by:** ⚖️ Adaeze (REVIEW-002 §6) · **Approver:** S1408661 (EL)
**Status of base decision:** unchanged. BVN-keyed permanent exclusion remains the target. This amendment records that it cannot be reached yet, and what ships in the meantime.

### Why

ADR-010's primary enforcement point is "at KYC submission". **There is no KYC module** — ADR-007 was approved and never built, and BVN is collected nowhere in the system (the only trace is the unused `bvn_pepper` in `config.py`). Enforcement point 2 explicitly delegates the block to point 1, so it is equally unreachable.

Meanwhile the consumer-facing responsible-play page asserted, until 2026-11-23, that a permanent BVN-keyed regime was live. It was not. The honest options were to build the registry or correct the copy; the copy was corrected, and this amendment commits to building what is buildable now.

### Amended decision

**Phase A — account-level exclusion. Buildable now; no BVN, no KYC dependency.**

1. **Registry key.** `self_exclusions` is keyed on `user_id` (PRIMARY KEY), with `bvn_hash` present as a **nullable UNIQUE** column from the first migration. The base decision's `bvn_hash TEXT PRIMARY KEY` is superseded. Phase B backfills the column; no second migration of a live table.
2. **Enforcement points amended.** The base decision named KYC submission, account creation and login. Added:
   - **Ticket purchase.** `ticket.service.issue_paid` refuses an excluded user. *This closes a defect in the base ADR, not merely in the code: purchase was never listed as an enforcement point, so a closed user holding a live session could buy a ticket.* Enforced at the service layer because the webhook reaches `issue_paid` without passing the route.
   - **Skill-question issue.** `skill.service.next_question` refuses an excluded user, so a doomed flow cannot be started.
   - **Login** is retained and is satisfied by existing code (`session_service` already refuses a user whose `status != 'active'`).
   - **Account creation** is retained as specified — registration is still permitted and still reveals nothing — but note it now provides **no** protection until Phase B, since the block it defers to does not exist.
3. **Wallet refund deferred.** The base decision requires the balance be refunded to the originating payment method, with escheatment where refund is impossible. **Neither capability exists:** there is no Paystack refund call (`payment/service.py` says so explicitly), and `docs/compliance/escheatment-policy.md` was never drafted. Phase A **holds** the balance on the closed account and surfaces it to support. Doing nothing while this ADR claims a refund occurs is precisely the defect this amendment exists to correct.

**Phase B — BVN-keyed cross-account enforcement. BLOCKED on ADR-007.**

Unchanged from the base decision. On delivery of KYC: hash with the existing pepper, backfill `bvn_hash`, add the pre-vendor lookup and the `self_exclusion.match` audit event.

### Invariants added

- A user with a `self_exclusions` row cannot obtain a ticket by **any** path. Asserted at the service layer, not only through HTTP.
- `self_exclusions` has exactly one writer: `atlas.identity.self_exclusion`.
- No un-exclude path exists in code or admin UI. V1 exclusion is permanent; absence of the capability is the enforcement.

### Consequence that must govern consumer copy

Phase A stops a user who asks to stop. **It does not prevent that user registering again with a different email and phone.** Copy may say the account can be permanently closed. Copy may **not** say a fresh account cannot bypass it until Phase B ships. The withdrawn sentence is recorded in REVIEW-002 §6.1.

### Base-decision invariants carried forward unchanged

BVN never stored in plaintext; exclusion lookup precedes every KYC vendor call; **the pepper is never rotated** — rotation invalidates the registry.

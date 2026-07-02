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

# ADR-012: Secret management via platform-native secret manager

**Status:** Proposed — pending EL approval
**Date:** 2026-06-29
**Approval:** _to be signed off by Engineering Lead_
**Reversibility:** Two-way door.

## Context

Atlas handles secrets for: Postgres connection strings, Paystack API keys, KYC vendor API keys, Sentry DSNs, JWT signing keys, the BVN hashing pepper (ADR-010), the server-seed encryption key (ADR-006), Bitcoin block explorer API keys, drand verification key fingerprint, S3 access keys, and the WhatsApp Business API token. The long-form PRD lists Vault as the V2+ option and "cloud KMS" generically. The V1 PRD (`PRD.md §4`) commits to the managed platform's native secret manager.

This ADR commits the secret-management mechanism and rotation policy.

## Decision

### V1 mechanism

All secrets live in the **managed platform's secret manager** (Fly secrets / AWS Secrets Manager / Render env vars with encryption at rest — final platform per Phase 0). Secrets are injected at process start as environment variables consumed by Pydantic Settings.

### Locality and access

- One secret store per environment: `dev`, `staging`, `production`. No cross-environment shared secrets.
- Local development uses a `.env.local` file (gitignored). A `.env.example` lists names only (no values).
- Production secrets are accessible only to the DevSecOps role on the platform; engineers do not have read access. Production debugging requires the time-bound `superadmin` grant flow per ADR-009.

### Categorisation and rotation cadence

| Secret class | Examples | Rotation cadence | Rotation owner |
|---|---|---|---|
| Vendor API keys | Paystack, KYC vendor, WhatsApp BSP, Sentry DSN | 90 days, or on suspected compromise | DevSecOps |
| Database credentials | Postgres primary, read replica | 30 days, automated via platform | DevSecOps |
| JWT signing key | Identity-module JWT | 90 days (rolling: new key issued; old key validated until expiry of last-issued JWT, max 14 days) | DevSecOps |
| Server-seed encryption key (ADR-006) | per-draw seed envelope key | Not rotated (key escrow risk vs operational risk) | DevSecOps; reviewed annually by Compliance |
| BVN hashing pepper (ADR-010) | self-exclusion pepper | **Not rotated** (rotation would invalidate the exclusion registry — see ADR-010) | Compliance Lead approval required for any change |
| S3 access keys | KYC document storage, audit-log archive | 90 days; per-bucket IAM roles preferred when platform supports | DevSecOps |

### Bootstrap

The Phase 0 environment setup runbook (`docs/runbooks/environment-bootstrap.md`) creates the initial secret set. The runbook is the authoritative reference; DevSecOps Agent maintains it.

### Application code conventions

- `backend/api/config.py` uses Pydantic Settings to read all secrets from env vars. Application code never reads env vars directly.
- A startup self-check verifies all required secrets are present and validates their shape (e.g. Paystack key starts with `sk_live_` in production). Missing or malformed secrets fail-fast on boot, not on first use.
- Secrets are never logged, never emitted in error messages, never sent to Sentry. Pydantic Settings is configured with `SecretStr` for all credential fields.
- CI secret scanning (gitleaks) runs on every PR; any committed secret fails the build.

### Disaster recovery

- The platform secret manager's backup/snapshot capability is the V1 backup. DevSecOps Agent verifies restorability quarterly.
- A break-glass procedure for catastrophic loss is documented in `docs/runbooks/secret-loss.md`. The BVN pepper and server-seed encryption keys are noted as "loss-impacting" — their permanent loss requires Compliance & Risk involvement to plan a path forward.

## Alternatives considered

- **HashiCorp Vault.** Lost for V1: operating Vault adds a critical-path service to manage; the platform's native solution meets V1 requirements at lower operational cost. Vault is a V2 candidate when multi-service or multi-cluster needs emerge.
- **Cloud KMS (AWS KMS, GCP KMS) directly, with application-side decryption.** Considered for the BVN pepper and server-seed encryption specifically. Acceptable but adds vendor dependency; deferred to V2 unless platform-native is insufficient.
- **In-database secrets with column-level encryption.** Lost: doesn't address the bootstrap problem (the encryption key must live somewhere); circular.
- **Per-engineer access to production secrets via a JIT system (e.g. Teleport).** Considered. Over-engineered for V1 team size; the time-bound `superadmin` grant via the audit-logged RBAC mechanism (ADR-009) is sufficient.

## Consequences

**Positive:**
- Zero infrastructure operated for secret management at V1 scale.
- Standard environment-variable injection means no application-code changes are needed when secrets rotate (process restart picks up new values).
- Rotation discipline is captured per secret class with clear ownership.

**Negative:**
- Vendor lock-in to the chosen managed platform's secret manager. Mitigated by the `config.py` abstraction — moving to Vault is changing how env vars get populated, not how the app reads them.
- Per-process startup must complete the secret self-check before serving traffic. Slightly slower startup; acceptable.
- The BVN pepper not being rotatable is a real constraint; documented as such in ADR-010 and surfaced here.

**Invariants:**
- No secret values in the git repo. Enforced by gitleaks in CI.
- No env-var reads outside `backend/api/config.py`. Enforced by CI grep.
- Production secrets are not accessible to engineering agents (or human engineers) by default. Audit-logged grants required.
- Rotation tickets are auto-filed by a scheduled job 14 days before each rotation due date.

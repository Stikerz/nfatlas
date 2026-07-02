# ADR-001: Modular monolith deployment topology

**Status:** Proposed — pending EL approval
**Date:** 2026-06-29 (amended 2026-07-02 with V0.5 demo topology addendum — see §V0.5)
**Approval:** _to be signed off by Engineering Lead_
**Reversibility:** Two-way door for V1 (single artefact, single platform). One-way door for V2+ once modules begin extraction.

## Context

V1 ships six business modules (Identity, Wallet & Ledger, Payment, Ticket, Draw Engine, Admin) plus a Flutter mobile app and a Next.js admin web. Team size at launch is small. Operational complexity is a real launch risk in a market with variable cloud infrastructure.

The long-form PRD assumes Kubernetes + Helm + Argo CD from day one. The V1 PRD explicitly cuts those (`PRD.md §4`) in favour of a managed platform. This ADR records the deployment topology that follows from that cut.

## Decision

V1 deploys as **three artefacts on one managed platform**:

1. **Backend service** — the FastAPI modular monolith. Single Docker image built from `infrastructure/docker/Dockerfile.backend`. All six modules live in this one process.
2. **Background worker** — same Docker image, different command. Polls the outbox table and runs scheduled jobs (reconciliation, free-entry transcription queue maintenance, scheduled draw lifecycle transitions). Sharing the image guarantees identical code paths between web requests and async work.
3. **Admin web** — the Next.js admin app, built and served as a static + SSR app. Built from `infrastructure/docker/Dockerfile.admin`.

The Flutter mobile app is distributed through TestFlight and Google Play, not deployed by the platform.

Managed-platform choice is finalised in Phase 0 (Fly.io, Railway, Render, or AWS App Runner). All four can host the three artefacts above plus a managed Postgres, managed Redis, and S3-compatible storage. Final choice records as ADR-001 amendment.

Environments: **dev** (local Docker Compose), **staging** (managed platform, auto-deploy from `main`), **production** (managed platform, manual deploy on EL approval).

## Alternatives considered

- **Kubernetes + Helm from day one.** Lost: operational load is too high for V1 team; one cluster outage at launch is a brand-damaging event. K8s is preserved as a V2 trigger in `delivery-framework.md §11` (trigger: managed platform cannot handle scale, or DR cluster genuinely needed).
- **Serverless (Lambda + API Gateway).** Lost: FastAPI's request lifecycle, the outbox worker pattern, and connection pooling against Postgres all fit a long-running process better than per-request cold-start functions. Also: vendor lock-in surface area too high for V1.
- **Multiple services from day one** (each module its own deployable). Lost: re-introduces the distributed-system tax (eventual consistency, retries, fanout) before the team has felt the monolith's pain. The modular-monolith-first stance (`PRD.md §4`) deliberately defers this.

## Consequences

**Positive:**
- One process to operate at launch. One log stream. One Sentry project per app.
- Module extraction in V2 is mechanical: the outbox (ADR-002) gives the eventual-consistency contract a future extracted service would need.
- Local dev mirrors production topology (same Docker image, same Postgres + Redis + S3 stack via Compose).

**Negative:**
- Scaling the monolith means scaling all modules together until extraction. Acceptable at V1 traffic volumes; revisit when one module dominates resource use.
- A bad deploy affects all modules. Mitigated by blue-green deploy (Phase 5) and the rollback drill (Phase 5 exit gate).
- A long-running background job in the worker process can interact poorly with the deploy lifecycle. Mitigated by keeping outbox processing idempotent (ADR-002) and individual jobs short.

**Forward-compat invariants:**
- Modules do not directly access each other's tables (enforced by grep in CI per `PRD.md §4`).
- Every state change emits an outbox event whose schema is in `docs/events.md`.

When these invariants hold, the path to V2 service extraction is a transport swap, not a redesign.

---

## V0.5 addendum (2026-07-02)

Founder decision on 2026-07-02: defer managed-platform commitment; build a working local demo (V0.5) first, primarily for investor demonstration. Full context in `_bmad-output/planning-artifacts/v0.5-demo-plan.md`.

**V0.5 topology (weeks 6–13 per amended `delivery-framework.md §2`):**

The three artefacts defined in §Decision (backend service, background worker, admin web) all run **locally under Docker Compose** on the founder's laptop. No managed-platform provisioning. Postgres and Redis run as Compose services rather than managed instances. S3 is not present in V0.5 (KYC document storage is stubbed since real KYC is deferred to Phase 3).

The architectural design of the modular monolith — module boundaries, ADR-002 outbox pattern, ADR-003 double-entry ledger invariants, ADR-005 audit-log invariants, ADR-006 commit-reveal protocol — is unchanged. Only the *deployment target* differs. The `Dockerfile.backend` and `Dockerfile.admin` built for V0.5 are the same images that later ship to managed-platform in Phase 5; only the compose file changes to platform primitives.

**When managed-platform provisioning happens:**

Deferred from Phase 2 to Phase 5 ("First cloud deployment" in the amended framework). The managed-platform choice (Fly.io, Railway, Render, AWS App Runner, or other) is a Phase 5-entry decision, not a Phase 0 decision. This ADR will be further amended at Phase 5 entry to record the specific platform selection.

**Why the demo-first pivot doesn't compromise the ADR:**

The forward-compat invariants in §Consequences remain the design contract for V0.5:
- Modules do not directly access each other's tables — same in V0.5.
- Every state change emits an outbox event — same in V0.5.

V0.5 code is a scoped subset of Phase 3 module implementation, not a parallel throwaway. Extending V0.5 → Phase 3 → Phase 5 deployment is additive on the same codebase.

**Consequences of the V0.5 topology, specific to this addendum:**

*Positive:*
- Zero cloud-vendor commitment during Phase 2. Reduces sunk cost if strategic pivot needed post-counsel-opinion.
- Founder can demo without any external dependencies except sandbox Paystack and public entropy sources.
- Onboarding a second engineer requires only Docker + Node + Python locally — no cloud account access, no secret provisioning.

*Negative:*
- V0.5 provides no evidence of how the stack behaves under managed-platform primitives (autoscaling, edge routing, platform observability). That validation moves to Phase 5, compressing that phase's risk window.
- Any managed-platform-specific integration (platform-native secret manager per ADR-012, platform-native logs per ADR-011) is not exercised in V0.5. Phase 5 will surface these integrations for the first time.
- Two-person production-secret rule (§Decision for staging/production) is not tested in V0.5 because there are no production secrets yet. Phase 5 operational drill must cover.

Neither consequence undermines the trust story V0.5 exists to tell.

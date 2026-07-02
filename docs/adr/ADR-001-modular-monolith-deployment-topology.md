# ADR-001: Modular monolith deployment topology

**Status:** Proposed — pending EL approval
**Date:** 2026-06-29
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

# ADR-011: Observability baseline (Sentry + platform logs/metrics in V1)

**Status:** Proposed — pending EL approval
**Date:** 2026-06-29
**Approval:** _to be signed off by Engineering Lead_
**Reversibility:** Two-way door. OpenTelemetry SDK in code means migrating to a self-hosted stack later is a config change, not a rewrite.

## Context

The long-form PRD lists Prometheus + Grafana + Loki + OpenTelemetry + Sentry from day one. The V1 PRD (`PRD.md §4`) cuts the self-hosted stack and commits to **OTel SDK in code + Sentry + the managed platform's built-in logs and metrics**, on the principle that V1 must operate reliably with the smallest viable surface area.

This ADR commits the V1 observability baseline and the V2 trigger to expand it.

## Decision

### V1 stack

| Concern | V1 mechanism |
|---|---|
| Error tracking | Sentry — backend, mobile, admin all configured with separate projects, source maps uploaded for admin, dSYMs for mobile |
| Structured logs | Backend writes JSON to stdout; platform aggregates and indexes for ~30 days (platform-default retention) |
| Metrics | Platform-native (request count, latency, CPU, memory, DB connections) for infra; application-emitted custom metrics deferred to OTel adoption |
| Traces | OpenTelemetry SDK present in backend code, emitting to platform's native exporter or to a no-op exporter. **A trace collector (Tempo / Jaeger / vendor) is NOT operated in V1** |
| Uptime monitoring | An external uptime monitor (e.g. UptimeRobot, Better Stack) pings `/healthz` and `/readyz` every minute |
| User analytics | Deferred to V2 |

### Code-level conventions

- Every request and outbox-dispatched event carries a `correlation_id`. Generated at the API boundary; logged on every emit; included in Sentry breadcrumbs.
- Every log line is JSON with at minimum: `ts`, `level`, `correlation_id`, `module`, `event`, `payload`.
- Sentry is configured with PII scrubbing for known PII fields (BVN, full names in payment metadata, document URLs).
- OpenTelemetry instrumentation:
  - `opentelemetry-instrumentation-fastapi`, `-sqlalchemy`, `-httpx` enabled.
  - Span attributes include `correlation_id`.
  - In V1, OTel emits to a no-op exporter by default and a stdout exporter in development; environment flag enables platform-native exporter when available.

### Dashboards (Phase 6 launch)

Owned by DevSecOps, built on the platform's native primitives:

- Payment success rate, payment volume (per Paystack rail).
- Ticket purchase rate, paid/free split per active draw.
- Draw engine lifecycle states (commits, closes, reveals per day).
- Ledger reconciliation status (yesterday's report).
- KYC queue depth.
- API p95/p99 latency.
- Error rate by endpoint.
- Sentry top issues this week.

### Alerts

- Payment success rate < 95% over 10 minutes → SEV-2 (PagerDuty)
- Ledger reconciliation mismatch (any) → SEV-1
- Audit-log chain verification failure → SEV-1
- Draw engine stuck in a state > 1 hour past scheduled transition → SEV-1
- API p95 > 500ms over 5 minutes → SEV-3 (Slack)
- Error rate > 1% over 5 minutes → SEV-2
- KYC queue > N pending (N set by Compliance) → SEV-3

Every alert links to a runbook in `docs/runbooks/`.

### V2 expansion triggers

(Echoed from `delivery-framework.md §11` for ADR self-containment.)

- **Self-hosted Prometheus + Grafana** → when platform-native metrics retention or cardinality limits become a problem.
- **Loki or ELK for log search** → when log volume outgrows platform-native search or when search needs (e.g. per-user trace reconstruction) outgrow JSON-grep.
- **Distributed tracing collector (Tempo / Jaeger / vendor)** → when modules begin extraction (i.e. when there are > 1 service to trace across).

## Alternatives considered

- **Full Prometheus + Grafana + Loki + OTel collector from day one.** Lost: significant operational load for a single-service V1; observability ops becomes a project of its own. The OTel SDK in code is the hedge — migration cost when triggers fire is small.
- **Vendor APM (Datadog, New Relic) instead of self-hosted later.** Considered: viable V2 option. ADR doesn't preclude it; the OTel SDK exports anywhere OTel-compatible.
- **No Sentry, rely on log search for errors.** Lost: error grouping, stack-trace deduplication, and release-tagging are exactly what Sentry does well; rebuilding them in log-grep is wasteful.

## Consequences

**Positive:**
- One vendor (Sentry) + platform-native = small operational surface.
- OTel SDK presence means V2 expansion is a config + exporter change.
- Correlation IDs end-to-end mean any reported issue is traceable from mobile app through backend modules to outbox to consumer.
- Alert runbooks force operational thinking to land before launch.

**Negative:**
- Platform-native log retention (typically 7–30 days) is shorter than self-hosted. Mitigation: critical audit information lives in `audit_log` (ADR-005), not in operational logs; operational logs are for incident triage only.
- Custom application metrics (e.g. "tickets purchased per minute per draw") require OTel collector to be useful; in V1 these can be derived from log queries or from the database. Acceptable tradeoff at V1 scale.
- Sentry-PII-scrubbing rules require maintenance as new modules add new fields. Compliance & Risk Agent reviews scrubbing config quarterly.

**Invariants:**
- Every API request carries a correlation ID, propagated to outbox events and consumer handlers. Enforced by middleware test.
- Sentry receives events from all three apps in staging before Phase 2 exit.
- Every alert has a corresponding runbook. Enforced by CI: a `docs/runbooks/` file must exist for every alert defined in the monitoring config.

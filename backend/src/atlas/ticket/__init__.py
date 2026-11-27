"""Ticket module (Week 5).

Owns: draw entries, skill-question responses, ticket artefact.

Self-exclusion enforcement (ADR-010) is NOT wired here — the
`self_exclusions` table and its checks do not exist yet. An earlier
docstring claimed otherwise; the claim was false and was removed
2026-11-23.

The free-entry route was unwired 2026-11-23 — see `models` for the
retained-schema rationale.
"""

"""Idempotency module (ADR-004).

Owns: `idempotency_records` table, middleware, per-endpoint dependency.
Day 2 lands middleware.py + dependency.py.

Every state-changing endpoint requires the `Idempotency-Key` header;
enforcement is contract-tested.
"""

"""Audit log module (ADR-005).

Owns: `audit_log` table, hash-chained writer, JCS canonicalization,
GENESIS row bootstrap. Day 2 will land writer.py.

Invariant: every write to `audit_log` from any module MUST go through
`atlas.audit_log.writer.append(...)`. CI grep enforces.
"""

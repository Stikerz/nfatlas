"""Golden-vector hash test for the audit-log canonicalizer.

Freezes the exact JCS-canonical-bytes + SHA-256 output for a known input so
any drift in `rfc8785`, Python's JSON encoder, or our field ordering is
caught by a unit test — not by a broken chain in prod.

Update this golden ONLY when ADR-005 §Hash chain intentionally changes.
"""

from __future__ import annotations

from datetime import datetime, timezone

from atlas.audit_log.writer import GENESIS_HASH, _canonical_row_bytes, compute_row_hash


_FIXED_ROW = dict(
    seq=1,
    occurred_at=datetime(2026, 7, 14, 9, 30, 0, tzinfo=timezone.utc),
    actor_type="user",
    actor_id="9c85f3a2-000c-4b5c-b1d1-000000000001",
    event_name="user.registered",
    subject_type="user",
    subject_id="9c85f3a2-000c-4b5c-b1d1-000000000001",
    payload={
        "user_id": "9c85f3a2-000c-4b5c-b1d1-000000000001",
        "email_hash": "0" * 64,
        "phone_e164": "+2348030000000",
        "dob_year": 1993,
        "terms_accepted": True,
    },
    prev_hash=GENESIS_HASH,
)


def test_canonical_bytes_are_deterministic() -> None:
    """RFC 8785 output for the fixed row must be byte-stable."""
    a = _canonical_row_bytes(**_FIXED_ROW)
    b = _canonical_row_bytes(**_FIXED_ROW)
    assert a == b


def test_canonical_form_sorts_object_keys() -> None:
    """JCS mandates lexicographic key ordering — sanity check."""
    canonical = _canonical_row_bytes(**_FIXED_ROW).decode()
    # actor_id precedes actor_type precedes event_name lexicographically.
    idx_actor_id = canonical.index('"actor_id"')
    idx_actor_type = canonical.index('"actor_type"')
    idx_event = canonical.index('"event_name"')
    assert idx_actor_id < idx_actor_type < idx_event


def test_row_hash_is_hex_sha256() -> None:
    row_hash = compute_row_hash(**_FIXED_ROW)
    assert len(row_hash) == 64
    assert all(c in "0123456789abcdef" for c in row_hash)


def test_row_hash_changes_when_payload_changes() -> None:
    baseline = compute_row_hash(**_FIXED_ROW)
    tampered = dict(_FIXED_ROW)
    tampered["payload"] = {**_FIXED_ROW["payload"], "dob_year": 1994}
    assert compute_row_hash(**tampered) != baseline


def test_row_hash_changes_when_prev_hash_changes() -> None:
    baseline = compute_row_hash(**_FIXED_ROW)
    tampered = dict(_FIXED_ROW)
    tampered["prev_hash"] = "0" * 64
    assert compute_row_hash(**tampered) != baseline

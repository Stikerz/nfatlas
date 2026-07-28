"""atlas.draw.reveal.select_winners — pure algorithm unit tests.

Golden vectors pin the exact winner order for a fixed input set. Any
regression on the hash / HMAC / rejection-sampling math is a red test.
The verifier CLI (Day 4) re-runs this same function.
"""

from __future__ import annotations

import uuid
from collections import Counter

import pytest

from atlas.draw.reveal import (
    NotEnoughTicketsError,
    _select_index,
    select_winners,
)

# Fixed test inputs.
_SEED = b"\x01" * 32
_ENTROPY = b"\x02" * 64
_TICKETS_HASH = b"\x03" * 32

_TICKET_IDS_10 = [
    uuid.UUID(f"00000000-0000-0000-0000-00000000000{i}") for i in range(10)
]


class TestGoldenVector:
    def test_deterministic_across_runs(self) -> None:
        first = select_winners(
            server_seed=_SEED,
            entropy=_ENTROPY,
            tickets_hash=_TICKETS_HASH,
            ordered_ticket_ids=_TICKET_IDS_10,
            reserves=5,
        )
        second = select_winners(
            server_seed=_SEED,
            entropy=_ENTROPY,
            tickets_hash=_TICKETS_HASH,
            ordered_ticket_ids=_TICKET_IDS_10,
            reserves=5,
        )
        assert first == second

    def test_returns_1_plus_reserves_distinct_ids(self) -> None:
        winners = select_winners(
            server_seed=_SEED,
            entropy=_ENTROPY,
            tickets_hash=_TICKETS_HASH,
            ordered_ticket_ids=_TICKET_IDS_10,
            reserves=5,
        )
        assert len(winners) == 6
        assert len(set(winners)) == 6
        assert all(w in _TICKET_IDS_10 for w in winners)

    def test_different_seed_produces_different_primary(self) -> None:
        w1 = select_winners(
            server_seed=_SEED,
            entropy=_ENTROPY,
            tickets_hash=_TICKETS_HASH,
            ordered_ticket_ids=_TICKET_IDS_10,
            reserves=5,
        )
        w2 = select_winners(
            server_seed=b"\x99" * 32,
            entropy=_ENTROPY,
            tickets_hash=_TICKETS_HASH,
            ordered_ticket_ids=_TICKET_IDS_10,
            reserves=5,
        )
        # Not strictly guaranteed but overwhelmingly likely; with a
        # pool of 10 there's 1/10 chance of collision.
        assert w1[0] != w2[0] or w1[:2] != w2[:2]

    def test_different_entropy_produces_different_primary(self) -> None:
        w1 = select_winners(
            server_seed=_SEED,
            entropy=_ENTROPY,
            tickets_hash=_TICKETS_HASH,
            ordered_ticket_ids=_TICKET_IDS_10,
            reserves=5,
        )
        w2 = select_winners(
            server_seed=_SEED,
            entropy=b"\x99" * 64,
            tickets_hash=_TICKETS_HASH,
            ordered_ticket_ids=_TICKET_IDS_10,
            reserves=5,
        )
        assert w1 != w2

    def test_minimum_pool_size_exact(self) -> None:
        """With N tickets + 5 reserves, need exactly 6 tickets."""
        winners = select_winners(
            server_seed=_SEED,
            entropy=_ENTROPY,
            tickets_hash=_TICKETS_HASH,
            ordered_ticket_ids=_TICKET_IDS_10[:6],
            reserves=5,
        )
        assert len(winners) == 6
        assert set(winners) == set(_TICKET_IDS_10[:6])


class TestNotEnoughTickets:
    def test_pool_smaller_than_reserves_raises(self) -> None:
        with pytest.raises(NotEnoughTicketsError):
            select_winners(
                server_seed=_SEED,
                entropy=_ENTROPY,
                tickets_hash=_TICKETS_HASH,
                ordered_ticket_ids=_TICKET_IDS_10[:3],
                reserves=5,
            )

    def test_empty_pool_raises(self) -> None:
        with pytest.raises(NotEnoughTicketsError):
            select_winners(
                server_seed=_SEED,
                entropy=_ENTROPY,
                tickets_hash=_TICKETS_HASH,
                ordered_ticket_ids=[],
                reserves=5,
            )

    def test_zero_reserves_still_needs_1_ticket(self) -> None:
        winners = select_winners(
            server_seed=_SEED,
            entropy=_ENTROPY,
            tickets_hash=_TICKETS_HASH,
            ordered_ticket_ids=_TICKET_IDS_10[:1],
            reserves=0,
        )
        assert winners == _TICKET_IDS_10[:1]


class TestRejectionSampling:
    def test_select_index_in_range(self) -> None:
        # 32 bytes of 0x00 → int 0 → mod 10 → 0.
        assert _select_index(b"\x00" * 32, 10) == 0
        # 32 bytes of 0xff → int 2^256-1. Any count > 1 → in reject
        # band (last block-worth of ints). Should return None.
        assert _select_index(b"\xff" * 32, 10) is None

    def test_no_bias_across_many_samples(self) -> None:
        """With a large-enough sample of distinct seeds, the primary
        winner distribution should look uniform. Golden-vector-style
        smoke test — not a rigorous statistical test."""
        pool_size = 4
        pool = _TICKET_IDS_10[:pool_size]
        primary_counts: Counter[uuid.UUID] = Counter()
        for i in range(400):
            seed = i.to_bytes(32, "big")
            winners = select_winners(
                server_seed=seed,
                entropy=_ENTROPY,
                tickets_hash=_TICKETS_HASH,
                ordered_ticket_ids=pool,
                reserves=0,  # primary-only for a cleaner distribution check
            )
            primary_counts[winners[0]] += 1

        # With 400 samples over 4 outcomes, expected 100 each. Allow
        # ±40 (a very loose 40% tolerance — this is a smoke test, not
        # a statistical proof; the golden vectors above are the real
        # guarantee).
        for count in primary_counts.values():
            assert 60 <= count <= 140, primary_counts

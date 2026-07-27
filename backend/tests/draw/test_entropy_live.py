"""atlas.draw.entropy — live-mode HTTP unit tests (mocked with pytest-httpx).

Live mode goes to real public endpoints in demo runs but must be
tested against deterministic mocks so CI stays fast + offline.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from atlas.draw.entropy import bitcoin, drand
from atlas.draw.entropy.protocol import (
    EntropyFetchError,
    EntropyMismatchError,
)


class TestBitcoinLive:
    async def test_matching_explorers_return_same_hash(self, httpx_mock) -> None:
        close_time = datetime(2026, 8, 4, 12, 0, 0, tzinfo=UTC)
        unix = int(close_time.timestamp())
        block_hash = "a" * 64
        # mempool.space single-shot.
        httpx_mock.add_response(
            method="GET",
            url=f"{bitcoin.MEMPOOL_BASE}/api/v1/mining/blocks/timestamp/{unix}",
            json={"height": 900_001, "hash": block_hash, "timestamp": unix},
        )
        # blockstream: tip height then a downward walk that stops
        # immediately (block at tip has timestamp ≥ unix, block at
        # tip-1 has timestamp < unix → tip is the answer).
        httpx_mock.add_response(
            method="GET",
            url=f"{bitcoin.BLOCKSTREAM_BASE}/api/blocks/tip/height",
            text="900001",
        )
        httpx_mock.add_response(
            method="GET",
            url=f"{bitcoin.BLOCKSTREAM_BASE}/api/block-height/900001",
            text=block_hash,
        )
        httpx_mock.add_response(
            method="GET",
            url=f"{bitcoin.BLOCKSTREAM_BASE}/api/block/{block_hash}",
            json={"id": block_hash, "height": 900_001, "timestamp": unix},
        )
        httpx_mock.add_response(
            method="GET",
            url=f"{bitcoin.BLOCKSTREAM_BASE}/api/block-height/900000",
            text="b" * 64,
        )
        httpx_mock.add_response(
            method="GET",
            url=f"{bitcoin.BLOCKSTREAM_BASE}/api/block/{'b' * 64}",
            json={"id": "b" * 64, "height": 900_000, "timestamp": unix - 600},
        )

        result = await bitcoin.fetch_live(close_time)
        assert result.block_hash == block_hash
        assert result.block_height == 900_001

    async def test_mismatched_explorers_raise(self, httpx_mock) -> None:
        close_time = datetime(2026, 8, 4, 12, 0, 0, tzinfo=UTC)
        unix = int(close_time.timestamp())
        httpx_mock.add_response(
            method="GET",
            url=f"{bitcoin.MEMPOOL_BASE}/api/v1/mining/blocks/timestamp/{unix}",
            json={"height": 900_001, "hash": "a" * 64, "timestamp": unix},
        )
        # blockstream returns a *different* hash.
        httpx_mock.add_response(
            method="GET",
            url=f"{bitcoin.BLOCKSTREAM_BASE}/api/blocks/tip/height",
            text="900001",
        )
        httpx_mock.add_response(
            method="GET",
            url=f"{bitcoin.BLOCKSTREAM_BASE}/api/block-height/900001",
            text="c" * 64,
        )
        httpx_mock.add_response(
            method="GET",
            url=f"{bitcoin.BLOCKSTREAM_BASE}/api/block/{'c' * 64}",
            json={"id": "c" * 64, "height": 900_001, "timestamp": unix},
        )
        httpx_mock.add_response(
            method="GET",
            url=f"{bitcoin.BLOCKSTREAM_BASE}/api/block-height/900000",
            text="d" * 64,
        )
        httpx_mock.add_response(
            method="GET",
            url=f"{bitcoin.BLOCKSTREAM_BASE}/api/block/{'d' * 64}",
            json={"id": "d" * 64, "height": 900_000, "timestamp": unix - 600},
        )

        with pytest.raises(EntropyMismatchError):
            await bitcoin.fetch_live(close_time)

    async def test_mempool_5xx_raises_fetch_error(self, httpx_mock) -> None:
        close_time = datetime(2026, 8, 4, 12, 0, 0, tzinfo=UTC)
        unix = int(close_time.timestamp())
        httpx_mock.add_response(
            method="GET",
            url=f"{bitcoin.MEMPOOL_BASE}/api/v1/mining/blocks/timestamp/{unix}",
            status_code=503,
        )
        with pytest.raises(EntropyFetchError, match=r"mempool\.space"):
            await bitcoin.fetch_live(close_time)


class TestDrandLive:
    async def test_fetch_matches_round_derivation(self, httpx_mock) -> None:
        close_time = datetime(2026, 8, 4, 12, 0, 0, tzinfo=UTC)
        expected_round = drand.round_at_or_after(close_time)
        randomness = "e" * 64
        signature = "f" * 192  # BLS12-381 sig is 96 bytes = 192 hex chars

        httpx_mock.add_response(
            method="GET",
            url=f"{drand.DRAND_API_BASE}/public/{expected_round}",
            json={
                "round": expected_round,
                "randomness": randomness,
                "signature": signature,
                "previous_signature": "0" * 192,
            },
        )
        result = await drand.fetch_live(close_time)
        assert result.round == expected_round
        assert result.randomness == randomness
        assert result.signature == signature

    async def test_wrong_round_in_response_raises(self, httpx_mock) -> None:
        close_time = datetime(2026, 8, 4, 12, 0, 0, tzinfo=UTC)
        expected_round = drand.round_at_or_after(close_time)
        httpx_mock.add_response(
            method="GET",
            url=f"{drand.DRAND_API_BASE}/public/{expected_round}",
            json={
                # Different round — proxy stale / bug.
                "round": expected_round + 5,
                "randomness": "e" * 64,
                "signature": "f" * 192,
            },
        )
        with pytest.raises(EntropyFetchError, match="returned round"):
            await drand.fetch_live(close_time)

    async def test_drand_5xx_raises_fetch_error(self, httpx_mock) -> None:
        close_time = datetime(2026, 8, 4, 12, 0, 0, tzinfo=UTC)
        expected_round = drand.round_at_or_after(close_time)
        httpx_mock.add_response(
            method="GET",
            url=f"{drand.DRAND_API_BASE}/public/{expected_round}",
            status_code=503,
        )
        with pytest.raises(EntropyFetchError, match="drand fetch failed"):
            await drand.fetch_live(close_time)

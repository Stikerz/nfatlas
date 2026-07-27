"""Bitcoin block-header entropy adapter (ADR-006 §Protocol stage 4).

Live mode fetches the first block whose timestamp is ≥ close_time from
two independent explorers (mempool.space + blockstream.info). Both
must return the same block hash — mismatch aborts the reveal.

Stub mode returns a deterministic SHA-256 of the close_time so tests
are reproducible without network.

Explorer API shapes used (public docs):
  - mempool.space
      GET /api/v1/mining/blocks/timestamp/{unix}  → {height, hash, timestamp}
  - blockstream.info
      GET /blocks/{tip_height}/status  → header block map
      Alt endpoint used here for parity:
      GET /blocks/tip/height           → int (current tip height)
      GET /block-height/{height}       → block hash (plain text)
      GET /block/{hash}                → block header (json with timestamp)

  For close_times in the past, mempool.space's `blocks/timestamp` is a
  single call. blockstream.info doesn't ship a "block-by-timestamp"
  endpoint; we walk the tip → find first block ≥ timestamp. V0.5
  demo close_times are days-old at reveal so the walk is bounded
  (~144 blocks/day; we walk ≤ 2 days). V1 replaces with an indexed
  service for arbitrary depth.
"""

from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any

import httpx

from atlas.draw.entropy.protocol import (
    BitcoinBlockEntropy,
    EntropyFetchError,
    EntropyMismatchError,
)

MEMPOOL_BASE = "https://mempool.space"
BLOCKSTREAM_BASE = "https://blockstream.info"
_TIMEOUT = httpx.Timeout(5.0, connect=3.0)


def _stub_block(close_time: datetime) -> BitcoinBlockEntropy:
    """Deterministic bitcoin entropy for tests + demo-offline runs.

    Hashes the ISO-8601 UTC representation of close_time so different
    draws see different values but re-runs of the same draw see the
    same value (verifier CLI stays reproducible).
    """
    seed = f"bitcoin-stub:{close_time.isoformat(timespec='microseconds')}"
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    # Fixed height so ordering is stable and the "block was mined at"
    # story lines up in the audit surface.
    return BitcoinBlockEntropy(
        block_height=900_000,
        block_hash=digest,
        block_timestamp=int(close_time.timestamp()),
    )


async def fetch_stub(close_time: datetime) -> BitcoinBlockEntropy:
    return _stub_block(close_time)


async def fetch_live(close_time: datetime) -> BitcoinBlockEntropy:
    """Cross-check two independent explorers; raise on mismatch.

    Both requests share a client for connection reuse.
    """
    unix = int(close_time.timestamp())
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        mempool = await _fetch_mempool(client, unix)
        blockstream = await _fetch_blockstream(client, unix)

    if mempool.block_hash != blockstream.block_hash:
        raise EntropyMismatchError(
            f"bitcoin explorers disagree at close_time={close_time.isoformat()}: "
            f"mempool={mempool.block_hash} vs blockstream={blockstream.block_hash}"
        )
    return mempool


async def _fetch_mempool(
    client: httpx.AsyncClient, unix: int
) -> BitcoinBlockEntropy:
    url = f"{MEMPOOL_BASE}/api/v1/mining/blocks/timestamp/{unix}"
    try:
        response = await client.get(url)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise EntropyFetchError(f"mempool.space fetch failed: {exc}") from exc

    data: dict[str, Any] = response.json()
    return BitcoinBlockEntropy(
        block_height=int(data["height"]),
        block_hash=str(data["hash"]),
        block_timestamp=int(data["timestamp"]),
    )


async def _fetch_blockstream(
    client: httpx.AsyncClient, unix: int
) -> BitcoinBlockEntropy:
    """Walk from tip until we find a block with timestamp >= unix.

    Bounded walk: bitcoin averages 10-min blocks (~144/day). For a
    close_time in the last 48h, the walk visits ≤ 288 blocks. V0.5
    demo close_times are always fresh. V1 replaces this with a
    timestamp-indexed service.
    """
    try:
        tip_response = await client.get(f"{BLOCKSTREAM_BASE}/api/blocks/tip/height")
        tip_response.raise_for_status()
        tip_height = int(tip_response.text.strip())
    except httpx.HTTPError as exc:
        raise EntropyFetchError(f"blockstream tip fetch failed: {exc}") from exc

    # Walk downward from tip, stopping at the first block with
    # timestamp < unix — the previous block is our answer.
    prev: BitcoinBlockEntropy | None = None
    for height in range(tip_height, max(0, tip_height - 300), -1):
        block = await _blockstream_at_height(client, height)
        if block.block_timestamp < unix:
            if prev is None:
                # close_time is in the future — no block yet.
                raise EntropyFetchError(
                    f"blockstream: no block found at or after unix={unix}"
                )
            return prev
        prev = block
    raise EntropyFetchError(
        f"blockstream: walked 300 blocks without crossing unix={unix}"
    )


async def _blockstream_at_height(
    client: httpx.AsyncClient, height: int
) -> BitcoinBlockEntropy:
    try:
        hash_response = await client.get(
            f"{BLOCKSTREAM_BASE}/api/block-height/{height}"
        )
        hash_response.raise_for_status()
        block_hash = hash_response.text.strip()

        block_response = await client.get(f"{BLOCKSTREAM_BASE}/api/block/{block_hash}")
        block_response.raise_for_status()
        block_data: dict[str, Any] = block_response.json()
    except httpx.HTTPError as exc:
        raise EntropyFetchError(f"blockstream block fetch failed: {exc}") from exc

    return BitcoinBlockEntropy(
        block_height=int(block_data["height"]),
        block_hash=str(block_data["id"]),
        block_timestamp=int(block_data["timestamp"]),
    )

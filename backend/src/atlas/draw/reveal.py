"""Winner selection — pure function per ADR-006 §Reserve algorithm.

Deterministic. Given the same inputs, `select_winners` always returns
the same ordered list. This is the load-bearing property for the
"provably fair" trust claim — the verifier CLI re-runs this same
function against the published proof inputs and reaches the same
winner.

Algorithm (per ADR-006 §Protocol stages 4-5):

    prng_seed = HMAC-SHA-256(key=server_seed, msg=entropy || tickets_hash)
    block(n)  = HMAC-SHA-256(key=prng_seed, msg=n.to_bytes(8, 'big'))
    for each 32-byte block, interpret big-endian as int; use
    rejection sampling (skip blocks ≥ largest multiple of ticket_count
    that fits in 2^256) so the modulo is unbiased. Take first N
    distinct indices in order → [primary, r1, r2, ..., rK].

Rejection sampling per week-6-build-plan §0 ask 3 — spec-correct
regardless of ticket count. Naive `int % n` would bias toward early
indices when 2^256 mod n ≠ 0.

Golden-vector tests in tests/draw/test_reveal_algorithm.py pin exact
outputs for a fixed input set — any behaviour change is a red test.
"""

from __future__ import annotations

import hashlib
import hmac
import uuid

_SHA256_BLOCK_MAX = 1 << 256  # 32-byte blocks interpreted as uint


class NotEnoughTicketsError(ValueError):
    """The ticket pool is smaller than 1 + reserves — no draw possible."""


def _prng_seed(*, server_seed: bytes, entropy: bytes, tickets_hash: bytes) -> bytes:
    """The HMAC key for the subsequent counter-based block stream."""
    return hmac.new(
        key=server_seed,
        msg=entropy + tickets_hash,
        digestmod=hashlib.sha256,
    ).digest()


def _block_at(seed: bytes, counter: int) -> bytes:
    """One 32-byte block from the deterministic stream."""
    return hmac.new(
        key=seed,
        msg=counter.to_bytes(8, "big"),
        digestmod=hashlib.sha256,
    ).digest()


def _select_index(block: bytes, count: int) -> int | None:
    """Rejection-sampled index in [0, count). Returns None if the block
    lands in the reject band; caller advances the counter and retries.

    The reject band is small — for realistic V1 counts of ~10^5,
    rejection probability is well under 10^-70 per block. For V0.5's
    tiny counts (1-10), effectively zero.
    """
    max_valid = (_SHA256_BLOCK_MAX // count) * count
    raw = int.from_bytes(block, "big")
    if raw >= max_valid:
        return None
    return raw % count


def select_winners(
    *,
    server_seed: bytes,
    entropy: bytes,
    tickets_hash: bytes,
    ordered_ticket_ids: list[uuid.UUID],
    reserves: int = 5,
) -> list[uuid.UUID]:
    """Return `[primary, r1, r2, ..., r_reserves]` — 1 + reserves
    distinct ticket ids in selection order.

    Raises NotEnoughTicketsError if the pool is too small to satisfy
    the requested reserves count.
    """
    needed = 1 + reserves
    n = len(ordered_ticket_ids)
    if n < needed:
        raise NotEnoughTicketsError(
            f"pool of {n} tickets cannot provide {needed} distinct winners"
        )

    seed = _prng_seed(
        server_seed=server_seed, entropy=entropy, tickets_hash=tickets_hash
    )
    picked_indices: list[int] = []
    picked_set: set[int] = set()
    counter = 0
    # Upper bound iterations to avoid infinite loop on pathological input.
    # In practice, converges in ~needed iterations for realistic pools.
    max_iterations = max(1000, needed * 100)
    while len(picked_indices) < needed and counter < max_iterations:
        idx = _select_index(_block_at(seed, counter), n)
        counter += 1
        if idx is None or idx in picked_set:
            continue
        picked_indices.append(idx)
        picked_set.add(idx)

    if len(picked_indices) < needed:
        # Effectively impossible with SHA-256 stream + rejection sampling
        # for any realistic n; leave the guard as a fail-loud.
        raise RuntimeError(
            f"exhausted {max_iterations} iterations without picking {needed} distinct indices"
        )

    return [ordered_ticket_ids[i] for i in picked_indices]

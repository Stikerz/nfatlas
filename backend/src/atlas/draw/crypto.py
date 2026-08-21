"""Symmetric encryption for `draws.server_seed_encrypted` — ADR-006 §Stage 1.

V0.5 stored the 32-byte server seed as plaintext hex (`week-5-build-plan §0
ask 5` — deferred to close the demo). Week 8 flips it to Fernet-encrypted
at rest, keyed from `ATLAS_SERVER_SEED_KEY` per ADR-012 §V1 mechanism.

Callers:
  - `atlas.draw.service.create_draw` — encrypts on commit.
  - `atlas.draw.service.reveal_draw` — decrypts to feed the winner-selection
    HMAC. The decrypted seed also lands in the `draw.revealed` audit event
    and the public /proof response (both are the reveal-phase disclosure,
    per ADR-006 §Stage 3).
  - `atlas.draw.routes.get_proof` — decrypts for the public proof surface.
  - `infrastructure/scripts/seed_v0_5.py` — encrypts the demo seed at write.

Forward-compat: the Fernet token stays valid as the inner-layer ciphertext
under a future cloud-KMS envelope (Phase 5 per ADR-012 §Alternatives).
"""

from __future__ import annotations

from cryptography.fernet import Fernet

from atlas.config import get_settings


def _fernet() -> Fernet:
    return Fernet(get_settings().server_seed_key.get_secret_value().encode())


def encrypt_server_seed(seed: bytes) -> str:
    """Encrypt a 32-byte server seed → Fernet token string.

    The token is url-safe base64 and safe to store in a `VARCHAR` column.
    Includes a random 128-bit IV so encrypting the same seed twice
    produces different ciphertext.
    """
    if not isinstance(seed, bytes):
        raise TypeError(f"expected bytes, got {type(seed).__name__}")
    if len(seed) != 32:
        raise ValueError(f"server seed must be 32 bytes, got {len(seed)}")
    return _fernet().encrypt(seed).decode()


def decrypt_server_seed(token: str) -> bytes:
    """Decrypt a Fernet token → 32-byte server seed.

    Raises `cryptography.fernet.InvalidToken` on tamper, wrong key, or
    malformed input. Callers should not catch this — a bad token means
    the row is unrecoverable and reveal must abort.
    """
    return _fernet().decrypt(token.encode())

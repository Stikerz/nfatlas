"""Fernet round-trip for server_seed_encrypted (ADR-006 §Stage 1)."""

from __future__ import annotations

import pytest
from cryptography.fernet import Fernet, InvalidToken

from atlas.draw import crypto


class TestEncryptDecrypt:
    def test_round_trip_preserves_seed(self) -> None:
        seed = b"\x01" * 32
        token = crypto.encrypt_server_seed(seed)
        assert crypto.decrypt_server_seed(token) == seed

    def test_ciphertext_is_fernet_token_shape(self) -> None:
        seed = b"\x02" * 32
        token = crypto.encrypt_server_seed(seed)
        assert token.startswith("gAAAAA")

    def test_two_encrypts_produce_different_ciphertext(self) -> None:
        """Fernet includes a random IV; same plaintext → different token."""
        seed = b"\x03" * 32
        assert crypto.encrypt_server_seed(seed) != crypto.encrypt_server_seed(seed)

    def test_tamper_is_rejected(self) -> None:
        seed = b"\x04" * 32
        token = crypto.encrypt_server_seed(seed)
        # Same guard as the JWT signature test: a fixed suffix is a no-op
        # when the token already ends with it. Only ~1 run in 64^4 here, but
        # it is the identical failure mode, so don't leave it loaded.
        tampered = token[:-4] + ("BBBB" if token.endswith("AAAA") else "AAAA")
        with pytest.raises(InvalidToken):
            crypto.decrypt_server_seed(tampered)

    def test_wrong_key_is_rejected(self, monkeypatch: pytest.MonkeyPatch) -> None:
        seed = b"\x05" * 32
        token = crypto.encrypt_server_seed(seed)

        other_key = Fernet.generate_key().decode()
        monkeypatch.setenv("ATLAS_SERVER_SEED_KEY", other_key)
        from atlas import config
        config.get_settings.cache_clear()
        try:
            with pytest.raises(InvalidToken):
                crypto.decrypt_server_seed(token)
        finally:
            config.get_settings.cache_clear()


class TestNonHexSeedRejected:
    def test_non_bytes_raises(self) -> None:
        with pytest.raises(TypeError):
            crypto.encrypt_server_seed("not bytes")  # type: ignore[arg-type]

    def test_wrong_length_raises(self) -> None:
        with pytest.raises(ValueError, match="32 bytes"):
            crypto.encrypt_server_seed(b"short")

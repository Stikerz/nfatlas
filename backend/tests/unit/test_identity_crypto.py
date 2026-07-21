"""Unit tests for the identity module's crypto primitives.

- OTP code generation entropy + hash round-trip.
- Password bcrypt round-trip.
- JWT encode/decode round-trip.

All plan §5 unit-test bullets covered here.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import jwt as pyjwt
import pytest

from atlas.identity import otp_service, password_service, session_service


class TestOTPCode:
    def test_length_and_digits(self) -> None:
        for _ in range(50):
            code = otp_service._generate_code()
            assert len(code) == otp_service.OTP_LENGTH
            assert code.isdigit()

    def test_entropy_reasonable(self) -> None:
        # 200 codes should have very few repeats given 10^6 space.
        codes = {otp_service._generate_code() for _ in range(200)}
        assert len(codes) >= 195

    def test_hash_is_deterministic(self) -> None:
        code = "123456"
        assert otp_service._hash_code(code) == otp_service._hash_code(code)

    def test_hash_changes_with_input(self) -> None:
        assert otp_service._hash_code("123456") != otp_service._hash_code("654321")


class TestPasswordBcrypt:
    def test_roundtrip(self) -> None:
        hashed = password_service.hash_password("correct horse battery staple")
        assert password_service.verify_password("correct horse battery staple", hashed)
        assert not password_service.verify_password("wrong password 1234", hashed)

    def test_hash_uses_configured_cost(self) -> None:
        hashed = password_service.hash_password("x" * 20)
        # bcrypt hash format: $2b$<cost>$<...>
        cost_field = hashed.split("$")[2]
        assert int(cost_field) == password_service.BCRYPT_COST

    def test_verify_returns_false_for_malformed_hash(self) -> None:
        assert not password_service.verify_password("anything", "not-a-bcrypt-hash")


class TestJWT:
    def test_roundtrip(self) -> None:
        session_id = uuid.uuid4()
        user_id = uuid.uuid4()
        expires_at = datetime.now(UTC) + timedelta(hours=8)
        token = session_service._encode_jwt(
            session_id=session_id, user_id=user_id, expires_at=expires_at
        )
        claims = session_service.decode_jwt(token)
        assert claims["iss"] == "atlas"
        assert claims["sub"] == str(user_id)
        assert claims["jti"] == str(session_id)

    def test_expired_token_rejected(self) -> None:
        session_id = uuid.uuid4()
        user_id = uuid.uuid4()
        expires_at = datetime.now(UTC) - timedelta(seconds=10)
        token = session_service._encode_jwt(
            session_id=session_id, user_id=user_id, expires_at=expires_at
        )
        with pytest.raises(pyjwt.ExpiredSignatureError):
            session_service.decode_jwt(token)

    def test_tampered_signature_rejected(self) -> None:
        session_id = uuid.uuid4()
        user_id = uuid.uuid4()
        expires_at = datetime.now(UTC) + timedelta(hours=8)
        token = session_service._encode_jwt(
            session_id=session_id, user_id=user_id, expires_at=expires_at
        )
        # Flip a character in the signature (last segment).
        header, payload, signature = token.split(".")
        tampered = f"{header}.{payload}.{'X' + signature[1:]}"
        with pytest.raises(pyjwt.InvalidTokenError):
            session_service.decode_jwt(tampered)

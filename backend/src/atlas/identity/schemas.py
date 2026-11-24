"""Identity request/response Pydantic schemas."""

from __future__ import annotations

import uuid
from datetime import date as date_
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

OTPPurpose = Literal["registration", "login_mfa"]


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    phone_e164: str = Field(pattern=r"^\+234[789]\d{9}$")
    date_of_birth: date_
    terms_accepted: bool

    @field_validator("terms_accepted")
    @classmethod
    def _must_accept_terms(cls, v: bool) -> bool:
        if v is not True:
            raise ValueError("terms_accepted must be true")
        return v


class RegisterResponse(BaseModel):
    user_id: uuid.UUID
    status: str


class OTPIssueRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    user_id: uuid.UUID
    purpose: OTPPurpose


class OTPIssueResponse(BaseModel):
    otp_id: uuid.UUID
    expires_at: datetime


class OTPVerifyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    user_id: uuid.UUID
    purpose: OTPPurpose
    code: str = Field(pattern=r"^\d{6}$")


class OTPVerifyResponse(BaseModel):
    verified: bool


class PasswordSetRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    password: str = Field(min_length=10, max_length=200)


class SessionCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    password: str = Field(min_length=1, max_length=200)


class SessionCreateResponse(BaseModel):
    session_id: uuid.UUID
    user_id: uuid.UUID
    access_token: str
    token_type: str = "Bearer"
    expires_at: datetime


class SessionCurrentResponse(BaseModel):
    session_id: uuid.UUID
    user_id: uuid.UUID
    email: str
    issued_at: datetime
    expires_at: datetime
    roles: list[str] = Field(default_factory=list)
    is_admin: bool = False


class SelfExcludeRequest(BaseModel):
    """ADR-010 §User-facing flow requires a typed confirmation plus an MFA
    challenge. `confirmation` must be the literal string EXCLUDE; `otp_code`
    is a `login_mfa` OTP the client requested immediately beforehand."""

    model_config = ConfigDict(extra="forbid")

    confirmation: Literal["EXCLUDE"]
    otp_code: str = Field(min_length=4, max_length=10)


class SelfExcludeResponse(BaseModel):
    """Deliberately states the Phase A limit back to the client so no
    surface can imply cross-account enforcement that does not exist.
    See the ADR-010 amendment of 2026-11-24."""

    user_id: uuid.UUID
    excluded_at: datetime
    sessions_revoked: int
    reversible: bool = False
    cross_account_enforced: bool = False


class SelfExclusionSummary(BaseModel):
    """Admin read-only view. Deliberately carries no action affordance —
    V1 has no reversal (ADR-010), so there is nothing an operator can do
    to a row beyond read it."""

    user_id: uuid.UUID
    email: str
    excluded_at: datetime
    excluded_by: str
    excluded_by_id: uuid.UUID | None
    reason: str | None
    bvn_enforced: bool = False


class SelfExclusionList(BaseModel):
    items: list[SelfExclusionSummary]

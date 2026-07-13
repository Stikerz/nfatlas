"""Identity request/response Pydantic schemas."""

from __future__ import annotations

import uuid
from datetime import datetime
from datetime import date as date_
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
    issued_at: datetime
    expires_at: datetime

"""Identity request/response Pydantic schemas."""

from __future__ import annotations

import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    phone_e164: str = Field(pattern=r"^\+234[789]\d{9}$")
    date_of_birth: date
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

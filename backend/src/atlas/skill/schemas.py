"""Skill-question request/response Pydantic schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SkillOption(BaseModel):
    """Option shown to the client — is_correct never crosses the boundary."""

    id: uuid.UUID
    text: str


class NextQuestionResponse(BaseModel):
    attempt_id: uuid.UUID
    question_id: uuid.UUID
    prompt: str
    options: list[SkillOption]
    expires_at: datetime


class AnswerRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    option_id: uuid.UUID


class AnswerResponse(BaseModel):
    attempt_id: uuid.UUID
    is_correct: bool
    entitlement_expires_at: datetime | None

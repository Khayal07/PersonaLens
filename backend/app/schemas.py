"""Pydantic request/response modelləri."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AuditRequest(BaseModel):
    content: str = Field(..., min_length=10, max_length=8000)
    content_type: str = Field(default="general", max_length=50)


class PersonaReactionOut(BaseModel):
    persona_id: str
    persona_name: str
    short_label: str
    ok: bool
    umumi_reaksiya: str = ""
    etibar_skoru: int | None = None
    narahatliqlar: list[str] = []
    diqqet_ceken_pozitiv: list[str] = []
    qerar: str = ""
    error: str | None = None


class AuditResponse(BaseModel):
    id: int
    content: str
    content_type: str
    created_at: datetime
    persona_reactions: list[PersonaReactionOut]
    synthesis: dict[str, Any]


class AuditSummary(BaseModel):
    id: int
    content: str
    content_type: str
    created_at: datetime

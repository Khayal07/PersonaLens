"""Pydantic request/response modelləri."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, model_validator


class AuditRequest(BaseModel):
    content: str | None = Field(default=None, max_length=8000)
    url: str | None = Field(default=None, max_length=2000)
    content_type: str = Field(default="general", max_length=50)

    @model_validator(mode="after")
    def _require_content_or_url(self) -> "AuditRequest":
        has_content = bool(self.content and self.content.strip())
        has_url = bool(self.url and self.url.strip())
        if not has_content and not has_url:
            raise ValueError("Ya mətn, ya da link daxil edilməlidir.")
        if has_content and len(self.content.strip()) < 10:
            raise ValueError("Mətn ən azı 10 simvol olmalıdır.")
        return self


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
    source_url: str | None = None
    created_at: datetime
    persona_reactions: list[PersonaReactionOut]
    synthesis: dict[str, Any]


class AuditSummary(BaseModel):
    id: int
    content: str
    content_type: str
    created_at: datetime

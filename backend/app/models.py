"""ORM modelləri — audit tarixçəsi və persona nəticələri."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Audit(Base):
    __tablename__ = "audits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), default="general")
    synthesis: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    persona_results: Mapped[list["PersonaResult"]] = relationship(
        back_populates="audit", cascade="all, delete-orphan"
    )


class PersonaResult(Base):
    __tablename__ = "persona_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    audit_id: Mapped[int] = mapped_column(ForeignKey("audits.id", ondelete="CASCADE"))
    persona_id: Mapped[str] = mapped_column(String(50))
    persona_name: Mapped[str] = mapped_column(String(100))
    # Persona reaksiyasının tam strukturu (orchestrator.PersonaReaction.to_dict).
    reaction: Mapped[dict] = mapped_column(JSON, default=dict)

    audit: Mapped["Audit"] = relationship(back_populates="persona_results")

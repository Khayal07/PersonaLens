"""FastAPI tətbiqi — /audit (POST), /audits (GET tarixçə), /audits/{id}.

Axın: content → orchestrator (5 paralel persona) → synthesizer → DB-yə yaz → cavab.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import get_db, init_db
from .models import Audit, PersonaResult
from .orchestrator import run_personas
from .schemas import (
    AuditRequest,
    AuditResponse,
    AuditSummary,
    PersonaReactionOut,
)
from .synthesizer import synthesize

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Marketing Mirror", version="1.0.0", lifespan=lifespan)

# Frontend nginx proxy ilə gəlir; lokal inkişaf üçün CORS açıq saxlanılır.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/audit", response_model=AuditResponse)
async def create_audit(req: AuditRequest, db: Session = Depends(get_db)) -> AuditResponse:
    # 1) 5 persona paralel
    reactions = await run_personas(req.content)
    # 2) sintez
    synthesis = await synthesize(req.content, reactions)

    # 3) DB-yə yaz
    audit = Audit(content=req.content, content_type=req.content_type, synthesis=synthesis)
    audit.persona_results = [
        PersonaResult(
            persona_id=r.persona_id,
            persona_name=r.persona_name,
            reaction=r.to_dict(),
        )
        for r in reactions
    ]
    db.add(audit)
    db.commit()
    db.refresh(audit)

    return AuditResponse(
        id=audit.id,
        content=audit.content,
        content_type=audit.content_type,
        created_at=audit.created_at,
        persona_reactions=[PersonaReactionOut(**r.to_dict()) for r in reactions],
        synthesis=synthesis,
    )


@app.get("/audits", response_model=list[AuditSummary])
def list_audits(db: Session = Depends(get_db), limit: int = 20) -> list[AuditSummary]:
    rows = db.scalars(
        select(Audit).order_by(Audit.created_at.desc()).limit(limit)
    ).all()
    return [
        AuditSummary(
            id=a.id,
            content=a.content,
            content_type=a.content_type,
            created_at=a.created_at,
        )
        for a in rows
    ]


@app.get("/audits/{audit_id}", response_model=AuditResponse)
def get_audit(audit_id: int, db: Session = Depends(get_db)) -> AuditResponse:
    audit = db.get(Audit, audit_id)
    if audit is None:
        raise HTTPException(status_code=404, detail="Audit tapılmadı")
    return AuditResponse(
        id=audit.id,
        content=audit.content,
        content_type=audit.content_type,
        created_at=audit.created_at,
        persona_reactions=[
            PersonaReactionOut(**pr.reaction) for pr in audit.persona_results
        ],
        synthesis=audit.synthesis,
    )

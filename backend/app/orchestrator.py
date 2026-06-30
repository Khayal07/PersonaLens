"""Orchestrator — 5 persona-nı paralel çağırır, nəticələri yığır.

Pattern: paralel persona call (asyncio.gather) → nəticələr toplanır →
(sonra synthesizer çağırılır, bax: synthesizer.py).

Bir persona uğursuz olarsa (parse xətası, rate-limit tükənməsi) bütün
audit dağılmır — həmin persona "uğursuz" kimi qeyd olunur, qalanları davam edir.
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field

from .llm_client import LLMClient
from .parsing import extract_json
from .personas import ALL_PERSONAS, Persona

logger = logging.getLogger("orchestrator")


@dataclass
class PersonaReaction:
    persona_id: str
    persona_name: str
    short_label: str
    ok: bool
    umumi_reaksiya: str = ""
    etibar_skoru: int | None = None
    narahatliqlar: list[str] = field(default_factory=list)
    diqqet_ceken_pozitiv: list[str] = field(default_factory=list)
    qerar: str = ""
    error: str | None = None

    def to_dict(self) -> dict:
        return {
            "persona_id": self.persona_id,
            "persona_name": self.persona_name,
            "short_label": self.short_label,
            "ok": self.ok,
            "umumi_reaksiya": self.umumi_reaksiya,
            "etibar_skoru": self.etibar_skoru,
            "narahatliqlar": self.narahatliqlar,
            "diqqet_ceken_pozitiv": self.diqqet_ceken_pozitiv,
            "qerar": self.qerar,
            "error": self.error,
        }


def _build_user_prompt(content: str) -> str:
    return (
        "Aşağıdakı marketinq mətnini öz perspektivindən qiymətləndir:\n\n"
        f"\"\"\"\n{content}\n\"\"\""
    )


async def _run_persona(
    client: LLMClient, persona: Persona, content: str
) -> PersonaReaction:
    try:
        raw = await client.complete(
            persona.full_system_prompt(), _build_user_prompt(content)
        )
        data = extract_json(raw)
        return PersonaReaction(
            persona_id=persona.id,
            persona_name=persona.name,
            short_label=persona.short_label,
            ok=True,
            umumi_reaksiya=str(data.get("umumi_reaksiya", "")).strip(),
            etibar_skoru=_safe_int(data.get("etibar_skoru")),
            narahatliqlar=_as_list(data.get("narahatliqlar")),
            diqqet_ceken_pozitiv=_as_list(data.get("diqqet_ceken_pozitiv")),
            qerar=str(data.get("qerar", "")).strip(),
        )
    except Exception as exc:  # noqa: BLE001 — qismi uğursuzluq tolere olunur
        logger.warning("Persona '%s' uğursuz oldu: %s", persona.id, exc)
        return PersonaReaction(
            persona_id=persona.id,
            persona_name=persona.name,
            short_label=persona.short_label,
            ok=False,
            error=str(exc),
        )


async def run_personas(content: str, client: LLMClient | None = None) -> list[PersonaReaction]:
    """Bütün persona-ları paralel çağırır və reaksiyaları qaytarır."""
    client = client or LLMClient()
    tasks = [_run_persona(client, p, content) for p in ALL_PERSONAS]
    return await asyncio.gather(*tasks)


def _safe_int(value) -> int | None:
    try:
        return max(0, min(100, int(value)))
    except (TypeError, ValueError):
        return None


def _as_list(value) -> list[str]:
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []

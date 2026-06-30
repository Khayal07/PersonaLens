"""Synthesizer Agent — 6-cı agent.

5 persona reaksiyasını toplayır, ümumi pattern-ləri tapır, konkret
düzəliş təklifləri və hər persona üçün uyğunlaşdırılmış alternativ variant verir.
"""
from __future__ import annotations

import json
import logging

from .llm_client import LLMClient
from .orchestrator import PersonaReaction
from .parsing import extract_json

logger = logging.getLogger("synthesizer")

SYSTEM_PROMPT = """
Sən təcrübəli marketinq strateqisən. Sənə eyni marketinq mətninə 5 fərqli
auditoriya persona-sının reaksiyaları verilir. Sənin işin tək-tək rəyləri
təkrarlamaq deyil — onları sintez edib ÜMUMİ PATTERN-ləri tapmaq və mətni
necə yaxşılaşdırmaq barədə konkret, əməli tövsiyə verməkdir.

Diqqət yetir:
- Neçə persona eyni problemi qaldırdı? (məs. "5-dən 3-ü qiymət görmədiyi
  üçün etibarsız hesab etdi")
- Hansı güclü tərəflər birdən çox persona tərəfindən qeyd olundu?
- Hansı dəyişiklik ən çox persona-ya təsir edəcək (yüksək prioritet)?

Cavabını YALNIZ aşağıdakı JSON formatında, Azərbaycan dilində ver.
Markdown və ya əlavə mətn olmasın:

{
  "umumi_qiymet": "<2-4 cümlə: mətnin ümumi vəziyyəti>",
  "ortaq_patternler": [
    {"pattern": "<təkrarlanan problem/güc>", "necə_persona": "<məs. 3/5>"}
  ],
  "prioritetli_düzelişler": [
    {"problem": "<konkret problem>", "tövsiyə": "<konkret həll>", "prioritet": "<yüksək|orta|aşağı>"}
  ],
  "persona_üçün_alternativ": [
    {"persona": "<persona adı>", "uyğunlaşdırılmış_mətn": "<bu persona-nı razı salan qısa alternativ cümlə/variant>"}
  ]
}
""".strip()


def _format_reactions(reactions: list[PersonaReaction]) -> str:
    blocks = []
    for r in reactions:
        if not r.ok:
            blocks.append(f"### {r.persona_name}\n(Bu persona texniki səbəbdən reaksiya vermədi.)")
            continue
        blocks.append(
            f"### {r.persona_name}\n"
            f"- Etibar skoru: {r.etibar_skoru}\n"
            f"- Qərar: {r.qerar}\n"
            f"- Ümumi reaksiya: {r.umumi_reaksiya}\n"
            f"- Narahatlıqlar: {'; '.join(r.narahatliqlar) or 'yoxdur'}\n"
            f"- Pozitivlər: {'; '.join(r.diqqet_ceken_pozitiv) or 'yoxdur'}"
        )
    return "\n\n".join(blocks)


def _build_user_prompt(content: str, reactions: list[PersonaReaction]) -> str:
    return (
        "ORİJİNAL MARKETİNQ MƏTNİ:\n"
        f"\"\"\"\n{content}\n\"\"\"\n\n"
        "5 PERSONA-NIN REAKSİYALARI:\n\n"
        f"{_format_reactions(reactions)}"
    )


async def synthesize(
    content: str, reactions: list[PersonaReaction], client: LLMClient | None = None
) -> dict:
    """Reaksiyaları sintez edib strukturlaşdırılmış tövsiyə qaytarır."""
    client = client or LLMClient()
    # Daha deterministik nəticə üçün aşağı temperatura.
    raw = await client.complete(
        SYSTEM_PROMPT, _build_user_prompt(content, reactions), temperature=0.3
    )
    try:
        return extract_json(raw)
    except (ValueError, json.JSONDecodeError) as exc:
        logger.warning("Synthesizer JSON parse olunmadı: %s", exc)
        # Fallback: ən azı xam mətni qaytar ki, istifadəçi tamamilə boş qalmasın.
        return {
            "umumi_qiymet": raw,
            "ortaq_patternler": [],
            "prioritetli_düzelişler": [],
            "persona_üçün_alternativ": [],
        }

"""Persona modeli və bütün persona-lar üçün ümumi output təlimatı.

Hər persona ayrı module-də öz `SYSTEM_PROMPT`-u ilə təyin olunur. Şəxsiyyət
mətnləri qəsdən fərqlidir — yüzeysel deyil, real narahatlıq nöqtələri.
Output formatı isə ortaqdır ki, orchestrator nəticələri eyni cür parse edə bilsin.
"""
from __future__ import annotations

from dataclasses import dataclass

# Bütün persona-lara əlavə olunan ümumi format təlimatı.
# Model yalnız JSON qaytarmalıdır ki, proqram cavabı etibarlı parse etsin.
OUTPUT_INSTRUCTION = """
Cavabını YALNIZ aşağıdakı JSON formatında, Azərbaycan dilində ver.
Başqa heç bir mətn, izah və ya markdown kod bloku əlavə etmə:

{
  "umumi_reaksiya": "<2-4 cümlə: mətni oxuyanda ilk reaksiyan>",
  "etibar_skoru": <0-100 arası tam ədəd: bu mətnə nə qədər inandın>,
  "narahatliqlar": ["<səni narahat edən konkret nöqtə>", "..."],
  "diqqet_ceken_pozitiv": ["<xoşuna gələn konkret nöqtə>", "..."],
  "qerar": "<biri: 'maraqlandım' | 'tərəddüdlüyəm' | 'imtina edirəm'>"
}
""".strip()


@dataclass(frozen=True)
class Persona:
    id: str
    name: str
    short_label: str
    system_prompt: str

    def full_system_prompt(self) -> str:
        return f"{self.system_prompt}\n\n{OUTPUT_INSTRUCTION}"

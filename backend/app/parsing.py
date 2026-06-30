"""LLM mətn cavabından JSON çıxarmaq üçün köməkçi.

Free-tier modellər bəzən JSON-u markdown kod bloku içində və ya əlavə
mətnlə qaytarır. Bu funksiya ən etibarlı şəkildə JSON obyektini ayırır.
"""
from __future__ import annotations

import json
import re
from typing import Any

_JSON_OBJECT = re.compile(r"\{.*\}", re.DOTALL)


def extract_json(text: str) -> dict[str, Any]:
    """Mətndən ilk JSON obyektini parse edir.

    Əvvəlcə birbaşa parse cəhdi, alınmazsa mətndən { ... } bloku axtarılır.
    Heç biri alınmazsa ValueError atılır.
    """
    text = text.strip()
    # ```json ... ``` çitlərini təmizlə.
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*", "", text).strip()
        text = text.rstrip("`").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = _JSON_OBJECT.search(text)
    if match:
        return json.loads(match.group(0))

    raise ValueError("Cavabda JSON tapılmadı")

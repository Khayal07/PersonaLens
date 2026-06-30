"""Model abstraction layer.

Bütün agent-lər (persona + synthesizer) yalnız `LLMClient.complete(...)`
interfeysi üzərindən LLM çağırır. Beləliklə provider/model dəyişikliyi
tək nöqtədə baş verir.

Free-tier modellərdə rate-limit (HTTP 429) tez-tez baş verdiyi üçün
eksponensial backoff ilə retry tətbiq olunur.
"""
from __future__ import annotations

import asyncio
import logging
import random

import httpx

from .config import Settings, get_settings

logger = logging.getLogger("llm")


class LLMError(Exception):
    """Retry-lərdən sonra da uğursuz olan LLM çağırışı."""


class LLMClient:
    """OpenRouter chat-completions üzərində nazik async wrapper."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float | None = None,
    ) -> str:
        """System + user prompt göndərir, model cavabını mətn kimi qaytarır.

        Retry logic: 429 və 5xx üçün eksponensial backoff + jitter.
        """
        payload = {
            "model": self.settings.openrouter_model,
            "temperature": (
                self.settings.llm_temperature if temperature is None else temperature
            ),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        headers = {
            "Authorization": f"Bearer {self.settings.openrouter_api_key}",
            "Content-Type": "application/json",
            # OpenRouter bu başlıqları tövsiyə edir (free-tier rate sayımı üçün).
            "HTTP-Referer": "https://github.com/Khayal07/PersonaLens",
            "X-Title": "Marketing Mirror",
        }
        url = f"{self.settings.openrouter_base_url}/chat/completions"

        last_error: Exception | None = None
        async with httpx.AsyncClient(timeout=self.settings.llm_timeout_seconds) as client:
            for attempt in range(1, self.settings.llm_max_retries + 1):
                try:
                    resp = await client.post(url, json=payload, headers=headers)
                    if resp.status_code == 429 or resp.status_code >= 500:
                        raise _RetryableStatus(resp.status_code, resp.text)
                    resp.raise_for_status()
                    data = resp.json()
                    # OpenRouter bəzən HTTP 200 ilə error payload qaytarır
                    # (məs. upstream rate-limit). Bunu da retry et.
                    if "choices" not in data:
                        code = data.get("error", {}).get("code", 0)
                        if code == 429 or (isinstance(code, int) and code >= 500):
                            raise _RetryableStatus(code or 503, str(data))
                        raise LLMError(f"LLM cavabında 'choices' yoxdur: {str(data)[:200]}")
                    return data["choices"][0]["message"]["content"].strip()
                except (_RetryableStatus, httpx.TransportError) as exc:
                    last_error = exc
                    if attempt == self.settings.llm_max_retries:
                        break
                    delay = min(2 ** attempt, 30) + random.uniform(0, 1)
                    logger.warning(
                        "LLM cəhd %d/%d uğursuz (%s) — %.1fs sonra retry",
                        attempt,
                        self.settings.llm_max_retries,
                        exc,
                        delay,
                    )
                    await asyncio.sleep(delay)
                except (KeyError, IndexError, ValueError) as exc:
                    # Gözlənilməz cavab formatı — retry mənasız.
                    raise LLMError(f"LLM cavabı parse olunmadı: {exc}") from exc

        raise LLMError(f"LLM çağırışı {self.settings.llm_max_retries} cəhddən sonra uğursuz: {last_error}")


class _RetryableStatus(Exception):
    def __init__(self, status: int, body: str) -> None:
        super().__init__(f"HTTP {status}: {body[:200]}")
        self.status = status

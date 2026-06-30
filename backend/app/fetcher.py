"""Link çəkici — rəsmi sayt/landing page URL-dən oxunaqlı mətn çıxarır.

İstifadəçi marketinq mətni yerinə link verə bilər. Burada səhifə HTML-i
çəkilir, naviqasiya/script/style təmizlənir və personaların qiymətləndirəcəyi
təmiz mətn qaytarılır.
"""
from __future__ import annotations

import logging
import re
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger("fetcher")

# Real brauzer kimi görünmək — bəzi saytlar bot User-Agent-i bloklayır.
_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
_TIMEOUT_SECONDS = 15.0
_MAX_CHARS = 6000
# Mətnə dəxli olmayan elementlər.
_STRIP_TAGS = ("script", "style", "nav", "footer", "header", "noscript", "svg", "form")


class FetchError(Exception):
    """Link çəkilə bilmədi — istifadəçiyə aydın mesaj üçün."""


def _validate_url(url: str) -> str:
    parsed = urlparse(url.strip())
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise FetchError("Düzgün link deyil. http(s):// ilə başlamalıdır.")
    return url.strip()


def _extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(_STRIP_TAGS):
        tag.decompose()
    text = soup.get_text(separator="\n")
    # Boş sətirləri yığ, artıq boşluqları təmizlə.
    lines = [ln.strip() for ln in text.splitlines()]
    text = "\n".join(ln for ln in lines if ln)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


async def fetch_page_text(url: str) -> str:
    """URL-dən təmizlənmiş mətn qaytarır. Uğursuzluqda FetchError atır."""
    url = _validate_url(url)
    try:
        async with httpx.AsyncClient(
            timeout=_TIMEOUT_SECONDS,
            follow_redirects=True,
            headers={"User-Agent": _USER_AGENT},
        ) as client:
            resp = await client.get(url)
    except httpx.TimeoutException as exc:
        raise FetchError("Sayt vaxtında cavab vermədi (timeout).") from exc
    except httpx.HTTPError as exc:
        raise FetchError(f"Sayta qoşulmaq alınmadı: {exc}") from exc

    if resp.status_code >= 400:
        raise FetchError(f"Sayt {resp.status_code} qaytardı, açıla bilmədi.")

    content_type = resp.headers.get("content-type", "")
    if "html" not in content_type and "text" not in content_type:
        raise FetchError("Link HTML səhifə deyil, mətn çıxarıla bilmədi.")

    text = _extract_text(resp.text)
    if len(text) < 50:
        raise FetchError(
            "Səhifədən mətn çıxmadı (JS-lə yüklənən sayt ola bilər)."
        )
    return text[:_MAX_CHARS]

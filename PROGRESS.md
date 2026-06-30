# PROGRESS — Marketing Mirror

Sessiyalar arası davamlılıq üçün. Hər fazadan sonra yenilənir.

## Status

- [x] **Faza 0 — Setup**: struktur, `.env.example`, `.gitignore`, `docker-compose.yml`, `PROGRESS.md`
- [x] **Faza 1 — LLM Abstraction Layer**: `LLMClient`, OpenRouter, retry/backoff
- [x] **Faza 2 — Persona Agentləri**: 5 persona module (fərqli system prompt)
- [x] **Faza 3 — Orchestrator**: `asyncio.gather` paralel + qismi uğursuzluq
- [x] **Faza 4 — Synthesizer**: pattern detection + tövsiyə generasiyası
- [x] **Faza 5 — Backend API**: FastAPI `/audit`, `/audits`, PostgreSQL ORM
- [x] **Faza 6 — Frontend**: HTML+CSS+JS, nginx proxy
- [x] **Faza 7 — Docker & E2E**: Dockerfiles, compose; LLM pipeline canlı test edildi
- [x] **Faza 8 — Sənədləşdirmə**: README + arxitektura diaqramı

## Qeydlər
- Stack: Python + FastAPI, PostgreSQL, OpenRouter free-tier, HTML+JS (nginx).
- Backend `:8000`, Frontend `:8080` (nginx `/api` → backend proxy).
- LLM output dili: Azərbaycan.
- İşləyən default model: `openai/gpt-oss-20b:free` (alternativ: `nvidia/nemotron-nano-9b-v2:free`).
- LLM axını DB-siz canlı test edildi: 5/5 persona + sintez işlədi.

- [x] **Link audit**: `fetcher.py` (BeautifulSoup) — rəsmi sayt URL-dən mətn çəkir.
      Schema `content` VƏ ya `url`; `Audit.source_url` sütunu; frontend URL inputu.

## Qalan / növbəti
- `docker-compose up --build` tam container testi: Docker Desktop işə salınmalıdır
  (test zamanı daemon bağlı idi). Kod, compose config və LLM axını yoxlanıldı.
- İstənərsə: pytest unit testləri, audit tarixçəsi üçün UI səhifəsi.

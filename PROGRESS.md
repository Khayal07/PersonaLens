# PROGRESS — Marketing Mirror

Sessiyalar arası davamlılıq üçün. Hər fazadan sonra yenilənir.

## Status

- [x] **Faza 0 — Setup**: struktur, `.env.example`, `.gitignore`, `docker-compose.yml`, `PROGRESS.md`
- [ ] **Faza 1 — LLM Abstraction Layer**: `LLMClient`, OpenRouter, retry
- [ ] **Faza 2 — Persona Agentləri**: 5 persona module
- [ ] **Faza 3 — Orchestrator**: paralel async call
- [ ] **Faza 4 — Synthesizer**: pattern + tövsiyə
- [ ] **Faza 5 — Backend API**: FastAPI `/audit`, PostgreSQL
- [ ] **Faza 6 — Frontend**: HTML+JS, nginx
- [ ] **Faza 7 — Docker & E2E**: `docker-compose up --build`
- [ ] **Faza 8 — Sənədləşdirmə**: README, diaqram

## Qeydlər
- Stack: Python + FastAPI, PostgreSQL, OpenRouter free-tier, HTML+JS (nginx).
- Backend `:8000`, Frontend `:8080` (nginx `/api` → backend proxy).
- LLM output dili: Azərbaycan.

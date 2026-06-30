# Plan: Marketing Mirror — Multi-Persona Content Audit Agent

## Context
Div Academy AI Engineering capstone. Marketinq mətnini (landing, sosial post,
reklam) 5 fərqli abituriyent persona-sı gözüylə simulyasiya edən, sonra
6-cı (synthesizer) agent ilə əməli düzəliş tövsiyələri çıxaran multi-agent
sistem. Greenfield layihə — repo boşdur (yalnız `.env`, `.gitignore`,
`marketing-mirror.md`). Remote: `github.com/Khayal07/PersonaLens`, branch `main`.

Qərarlar: Frontend = minimal HTML+JS (FastAPI static, tək container).
LLM output dili = Azərbaycan dili. AI provider = OpenRouter free-tier.

## Layihə Strukturu
Backend və frontend tam ayrı top-level qovluqlar. Hər biri öz Docker
container-i. Frontend nginx ilə verilir, backend-ə `/audit` üzərindən
fetch edir (nginx reverse proxy `/api` → backend).
```
PersonaLens/
├── docker-compose.yml
├── .env / .env.example
├── PROGRESS.md
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py            # FastAPI app, /audit, /audits
│       ├── config.py         # env + model config
│       ├── llm_client.py     # LLMClient abstraction (OpenRouter)
│       ├── orchestrator.py   # paralel persona call + synthesizer
│       ├── personas/         # 5 persona modulu (system prompt + meta)
│       ├── synthesizer.py
│       ├── db.py             # SQLAlchemy engine/session
│       ├── models.py         # ORM: audit, persona_result
│       └── schemas.py        # Pydantic request/response
└── frontend/
    ├── Dockerfile            # nginx:alpine
    ├── nginx.conf            # /api → backend reverse proxy
    ├── index.html
    └── app.js
```

## İcra Mərhələləri

### Faza 0 — Setup
- Qovluq strukturu, `.env.example` (OPENROUTER_API_KEY, OPENROUTER_MODEL, DB creds).
- `.gitignore`-a `__pycache__`, `node_modules`, `.env` (artıq var) əlavə.
- `docker-compose.yml` skeleti (backend + postgres servisi).
- `PROGRESS.md` yaradılması.
- Commit: `Phase 0: project scaffold`.

### Faza 1 — Model Abstraction Layer (`llm_client.py`, `config.py`)
- `LLMClient` class: vahid `complete(system, user) -> str` interfeysi.
- OpenRouter `httpx` async POST `chat/completions`.
- Model adı config-dən (`OPENROUTER_MODEL`), default free model.
- Error handling + retry (exponential backoff, 429 rate-limit üçün vacib).
- Commit: `Phase 1: LLM abstraction layer`.

### Faza 2 — Persona Agentləri (`personas/`)
- Hər persona ayrı module: `id`, `name`, `SYSTEM_PROMPT`.
- 5 persona spec-dəki kimi, real fərqli şəxsiyyət/narahatlıq (generic deyil),
  Azərbaycan dilində reaksiya. Output strukturlu (reaksiya + etibar siqnalı).
- `personas/__init__.py`-da `ALL_PERSONAS` siyahısı (orchestrator üçün).
- Commit: `Phase 2: persona agents`.

### Faza 3 — Orchestrator (`orchestrator.py`)
- `asyncio.gather` ilə 5 persona-nı paralel çağır.
- Nəticələri yığ, qismi uğursuzluğu idarə et (bir persona düşsə davam et).
- Commit: `Phase 3: orchestrator`.

### Faza 4 — Synthesizer (`synthesizer.py`)
- 5 reaksiyanı toplayıb pattern tapan prompt (məs. "3/5 qiymət görmədi").
- Konkret düzəlişlər + hər persona üçün uyğunlaşdırılmış alternativ.
- Commit: `Phase 4: synthesizer`.

### Faza 5 — Backend API (`main.py`, `db.py`, `models.py`, `schemas.py`)
- `POST /audit`: content qəbul → orchestrator → synthesizer → nəticə.
- PostgreSQL: `audit` + `persona_result` cədvəlləri, hər audit saxlanır.
- `GET /audits`: tarixçə.
- CORS / nginx proxy ilə frontend-dən çağırış.
- Startup-da `Base.metadata.create_all` (sadə, migration-suz).
- Commit: `Phase 5: FastAPI backend + DB`.

### Faza 6 — Frontend (ayrı `frontend/` qovluğu)
- Mətn daxiletmə sahəsi + Submit.
- 5 persona reaksiyası kart şəklində, synthesizer nəticəsi aşağıda.
- `fetch('/api/audit')`, loading state. Saf JS, framework yox.
- `nginx.conf`: static verir + `/api` → backend proxy.
- Commit: `Phase 6: frontend`.

### Faza 7 — Docker & End-to-End
- `backend/Dockerfile` (python:3.12-slim, uvicorn).
- `frontend/Dockerfile` (nginx:alpine).
- `docker-compose.yml`: 3 servis — postgres, backend, frontend.
- `docker-compose up --build` ilə hamısı bir komanda ilə qalxsın.
- DB hazır olana qədər gözləmə (healthcheck / retry connect).
- E2E test: frontend → nümunə mətn → 5 kart + sintez görünsün.
- Commit: `Phase 7: docker + e2e`.

### Faza 8 — Sənədləşdirmə
- `README.md`: qurulum, istifadə, arxitektura diaqramı, model dəyişdirmə.
- `PROGRESS.md` final yenilənmə.
- Commit: `Phase 8: docs`.

## Yenidən İstifadə / Qeydlər
- Sıfırdan layihə — mövcud kod yoxdur, hər şey yeni yazılır.
- `LLMClient` tək nöqtə: model abstraksiyası burada (spec tələbi).
- Hər personanın system prompt-u fərqli — generic template-dən qaçılır.
- Git: hər fazadan sonra commit + push `origin/main`.

## Verification
- `docker-compose up --build` → xəta olmadan qalxır.
- Brauzer `localhost:8000` → mətn daxil et → `/audit` 5 persona kartı + sintez.
- `POST /audit` curl ilə yoxla → JSON-da 5 persona + synthesizer.
- `GET /audits` → əvvəlki audit-lər DB-dən qayıdır.
- Rate-limit: retry log-da görünür, sistem çökmür.

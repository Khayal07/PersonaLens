# Marketing Mirror — Multi-Persona Content Audit Agent

Marketinq mətnini (landing page, sosial media postu, reklam) **5 fərqli
namizəd tələbə persona-sı** gözüylə simulyasiya edib audit edən multi-agent sistem.
6-cı (synthesizer) agent bu reaksiyaları sintez edib konkret, əməli düzəliş
tövsiyələri çıxarır.

> Div Academy AI Engineering kursu capstone layihəsi.

---

## Arxitektura

```
                ┌─────────────────────────────────────────────┐
                │                 Frontend (nginx)             │
                │   index.html · app.js · /api → proxy         │
                └───────────────────────┬─────────────────────┘
                                        │  POST /api/audit
                                        ▼
                ┌─────────────────────────────────────────────┐
                │            Backend (FastAPI :8000)           │
                │                                              │
                │   /audit ──► Orchestrator                    │
                │                  │  asyncio.gather (paralel) │
                │     ┌────────────┼────────────┐             │
                │     ▼   ▼   ▼   ▼   ▼  (5 persona agenti)    │
                │   Büdcə│Karyera│Xaric│Skeptik│Data           │
                │     └────────────┬────────────┘             │
                │                  ▼                           │
                │            Synthesizer Agent                 │
                │          (pattern + tövsiyə)                 │
                │                  │                           │
                │                  ▼                           │
                │   LLMClient ──► OpenRouter (free-tier)       │
                │                  │                           │
                │                  ▼                           │
                │             PostgreSQL (audit tarixçəsi)     │
                └─────────────────────────────────────────────┘
```

### 6 Agent
1. **Büdcə Məhdud Abituriyent** — qiymət şəffaflığı, ROI, valideyn təzyiqi.
2. **Karyera Dəyişdirən (28)** — vaxt, iş bazarı nəticəsi, risk.
3. **Xaricdə Oxumaq İstəyən** — beynəlxalq tanınma, dil, sertifikat dəyəri.
4. **Skeptik, Yorulmuş İstifadəçi** — klişe detektoru, etibarsızlıq siqnalları.
5. **Data-Driven Qərar Verən** — rəqəm, sübut, müqayisə; boş iddiaları qeyd edir.
6. **Synthesizer** — 5 reaksiyanı toplayır, ortaq pattern-ləri tapır, prioritetli
   düzəlişlər və hər persona üçün uyğunlaşdırılmış alternativ təklif edir.

**Koordinasiya:** orchestrator pattern — 5 persona paralel çağırılır
(`asyncio.gather`), nəticələr yığılır, sonra synthesizer çağırılır.

---

## Texniki Stack

| Layer | Texnologiya |
|-------|-------------|
| Backend | Python 3.12 + FastAPI |
| DB | PostgreSQL 16 (audit tarixçəsi, persona nəticələri) |
| AI | OpenRouter API — **yalnız free-tier modellər** |
| Frontend | Saf HTML + CSS + JS, nginx ilə verilir |
| Infra | Docker + docker-compose (3 servis) |

---

## Sürətli başlanğıc

### 1. Tələblər
- Docker Desktop (işləyən vəziyyətdə)
- OpenRouter API açarı — https://openrouter.ai/keys

### 2. Konfiqurasiya
```bash
cp .env.example .env
# .env içində OPENROUTER_API_KEY-i öz açarınla əvəz et
```

### 3. İşə salma
```bash
docker-compose up --build
```

| Servis | Ünvan |
|--------|-------|
| Frontend | http://localhost:8080 |
| Backend API | http://localhost:8000 |
| API sənədləri | http://localhost:8000/docs |

Brauzerdə `localhost:8080` aç → mətni yapışdır → **Audit et**.

---

## Model dəyişmək

Model adı **yalnız `.env`**-dən idarə olunur (`OPENROUTER_MODEL`). Kodu
dəyişmədən istənilən free modelə keç:

```env
OPENROUTER_MODEL=nvidia/nemotron-nano-9b-v2:free
```

Bütün agent-lər vahid `LLMClient` interfeysi üzərindən işləyir
(`backend/app/llm_client.py`), ona görə provider/model dəyişikliyi tək nöqtədədir.

> **Qeyd:** Free-tier modellər upstream rate-limit-ə (HTTP 429) düşə bilər.
> `LLMClient` eksponensial backoff ilə retry edir; bir persona uğursuz olsa belə
> audit dağılmır, qalan persona-lar davam edir.

---

## API

| Method | Endpoint | Təsvir |
|--------|----------|--------|
| POST | `/audit` | Mətni audit et → 5 persona + sintez |
| GET | `/audits` | Audit tarixçəsi (son 20) |
| GET | `/audits/{id}` | Konkret audit detalı |
| GET | `/health` | Sağlamlıq yoxlaması |

**Nümunə:**
```bash
curl -X POST http://localhost:8000/audit \
  -H "Content-Type: application/json" \
  -d '{"content":"Həyatını dəyiş! 3 ayda developer ol.","content_type":"ad"}'
```

---

## Layihə strukturu

```
PersonaLens/
├── docker-compose.yml         # postgres + backend + frontend
├── .env / .env.example
├── PROGRESS.md
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py            # FastAPI endpoints
│       ├── config.py          # env + model konfiqurasiyası
│       ├── llm_client.py      # LLMClient abstraction + retry
│       ├── orchestrator.py    # 5 persona paralel
│       ├── synthesizer.py     # sintez agenti
│       ├── personas/          # 5 persona modulu
│       ├── parsing.py         # LLM cavabından JSON çıxarma
│       ├── db.py · models.py · schemas.py
└── frontend/
    ├── Dockerfile · nginx.conf
    └── index.html · styles.css · app.js
```

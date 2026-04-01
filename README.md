# CS Learning Map — Adaptive Learning System

A "Google Maps for Learning" adaptive CS education platform built on:

- **Bayesian Knowledge Tracing (BKT)** — probabilistic per-KC mastery estimation
- **Prerequisite Graph** — DAG of CS concepts with dependency constraints
- **Routing Engine** — backward BFS + topological sort to generate personalized learning paths
- **Decision Policy** — advance / remediate / reroute based on mastery thresholds

## Architecture

```
Frontend (Next.js 14 + React Flow)  ←→  Backend (FastAPI + Python)  ←→  PostgreSQL
```

Full **as-built system design** (data model, APIs, flows, mapping to the research spec): [docs/SYSTEM_DESIGN.md](docs/SYSTEM_DESIGN.md).

## Prerequisites

- **Path A (Docker):** [Docker](https://docs.docker.com/get-docker/) with Docker Compose v2.
- **Path B (local processes):** Docker (for Postgres only), **Python 3.12+**, **Node.js 20+**, and `npm`.

## Quick Start

### Path A — Full stack with Docker (simplest)

Starts PostgreSQL, FastAPI backend, Next.js frontend (production build), and pgAdmin.

```bash
docker compose up --build
# or detached: docker compose up --build -d
```

| Service | URL / port | Notes |
|--------|------------|--------|
| Web app | [http://localhost:3000](http://localhost:3000) | Next.js |
| API + Swagger | [http://localhost:8000](http://localhost:8000), `/docs` | FastAPI |
| PostgreSQL (host) | `localhost:5434` | User/password/db: `postgres` / `postgres` / `cs_learning` |
| pgAdmin | [http://localhost:5050](http://localhost:5050) | Email `admin@admin.com`, password `admin` |

On startup the **backend** container runs **Alembic migrations** and the **idempotent seed** script, then Uvicorn ([`backend/docker-entrypoint.sh`](backend/docker-entrypoint.sh)).

### Path B — Local backend + frontend, database in Docker

**1. Start PostgreSQL only**

```bash
docker compose up -d db
```

Use `DATABASE_URL=postgresql://postgres:postgres@localhost:5434/cs_learning` in `backend/.env` (see [`backend/.env.example`](backend/.env.example)).

**2. Backend**

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
python -m app.seed.seed_data
uvicorn app.main:app --reload --port 8000
# Swagger UI: http://localhost:8000/docs
```

**3. Frontend**

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
# App: http://localhost:3000
```

### Run backend tests

```bash
cd backend && pytest tests/ -v
```

## Seed Data

7 Knowledge Components (KCs) with prerequisite graph:

```
Variables → Boolean Expressions → Conditionals → Loops → Functions → Recursion
                                                       ↘ Arrays / Lists → Recursion
```

28+ multiple-choice quiz items (3–5 per KC), Python-focused.

## BKT Parameters (defaults from Corbett & Anderson 1995)

| Parameter | Default | Meaning |
|-----------|---------|---------|
| P(L0) | 0.10 | Prior mastery probability |
| P(T)  | 0.10 | Learning rate per attempt |
| P(G)  | 0.25 | Guess probability |
| P(S)  | 0.10 | Slip probability |
| τ_mastery | 0.95 | Advance threshold |
| τ_low | 0.40 | Reroute threshold |
| k | 3 | Attempts before reroute eligible |

## Screens

| Screen | Path | Purpose |
|--------|------|--------|
| Landing | `/` | Enter learner name |
| Goal | `/goal` | Select target KC |
| Map | `/map` | Interactive React Flow knowledge graph |
| Practice | `/activity` | Answer questions, see BKT updates |
| Progress | `/progress` | Mastery per KC + attempt history |
| Admin | `/admin` | Manage KCs, items, prereq edges |

## API Endpoints

Base URL: `http://localhost:8000`  
Swagger: `http://localhost:8000/docs`

Key endpoints:

- `GET /api/v1/kcs/graph` — full KC + edge graph for visualization
- `GET /api/v1/items/next?learner_id=&kc_id=` — next quiz item
- `POST /api/v1/attempts` — submit answer → BKT update → decision
- `GET /api/v1/mastery?learner_id=` — all KC masteries with status
- `POST /api/v1/routes` — create learning route toward goal KC
- `POST /api/v1/routes/{id}/advance` — advance after KC mastered
- `POST /api/v1/routes/{id}/reroute` — backtrack to prerequisite
- `DELETE /api/v1/mastery/{id}` — reset learner progress (demo)
- `POST /api/v1/tutor/chat` — optional AI tutor (`LLM_PROVIDER`: anthropic | openai | gemini; does not change routing)

Route and attempt responses include plain-language **why-next** / **decision** rationale fields for the UI.

## AI tutor (optional)

The app defaults to **Anthropic Claude** for the tutor. The tutor only returns text; **routing and BKT are unchanged**.

**Claude setup (recommended):**

1. Copy [`backend/.env.example`](backend/.env.example) to `backend/.env` if you have not already.
2. Create an API key at [Anthropic Console](https://console.anthropic.com/).
3. Set `ANTHROPIC_API_KEY` in `backend/.env`. Defaults: `LLM_PROVIDER=anthropic`, `ANTHROPIC_MODEL=claude-sonnet-4-6` (override with e.g. `claude-haiku-4-5` for lower cost/latency — see [Anthropic models](https://docs.anthropic.com/en/docs/about-claude/models)).
4. Restart the backend. Use the **AI tutor** panel on Map and Practice.

| Provider | Required env vars | Notes |
|----------|-------------------|--------|
| `anthropic` (default) | `ANTHROPIC_API_KEY`, optional `ANTHROPIC_MODEL`, `ANTHROPIC_API_URL`, `ANTHROPIC_VERSION` | [Claude Messages API](https://docs.anthropic.com/en/api/messages) |
| `openai` | `LLM_API_KEY` (or `OPENAI_API_KEY`), optional `LLM_BASE_URL`, `LLM_MODEL` | OpenAI or OpenAI-compatible `POST /v1/chat/completions` |
| `gemini` | `GEMINI_API_KEY`, optional `GEMINI_MODEL`, `GEMINI_API_BASE_URL` | [Gemini generateContent](https://ai.google.dev/api/generate-content) |

Also: `LLM_TIMEOUT_SEC` (optional, default 60).

**Docker:** Compose loads `backend/.env` when present (`env_file` with `required: false` in [`docker-compose.yml`](docker-compose.yml)). Add your `ANTHROPIC_API_KEY` there for the tutor in containers. Never commit API keys.

## Research PDF (LaTeX)

Source and build steps: [docs/research/README.md](docs/research/README.md).

## References

- Corbett & Anderson (1995) — Bayesian Knowledge Tracing
- VanLehn (2006) — Outer/Inner loop in ITS
- Brusilovsky (2001) — Adaptive Hypermedia
- Piech et al. (2015) — Deep Knowledge Tracing

## Submission checklist

Before handing in the project, verify:

- [ ] `cd backend && pytest tests/ -v` passes
- [ ] `cd frontend && npm run lint` and `npm run build` pass
- [ ] Path A or Path B from **Quick Start** runs end-to-end (open app, goal, map, one practice attempt)
- [ ] If submitting the research PDF: `pdflatex` twice on `docs/research/research-plan.tex` (see [docs/research/README.md](docs/research/README.md))
- [ ] No secrets or `.env` files committed (`.env` is gitignored)

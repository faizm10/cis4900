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

## Quick Start

### 1. Start PostgreSQL
```bash
docker compose up -d
```

### 2. Backend
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
python -m app.seed.seed_data
uvicorn app.main:app --reload --port 8000
# Swagger UI: http://localhost:8000/docs
```

### 3. Frontend
```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
# App: http://localhost:3000
```

### 4. Run backend tests
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
|--------|------|---------|
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
- `POST /api/v1/tutor/chat` — optional AI tutor (`LLM_PROVIDER`: openai | anthropic | gemini; does not change routing)

Route and attempt responses include plain-language **why-next** / **decision** rationale fields for the UI.


## AI tutor (optional)

Set `LLM_PROVIDER` in `backend/.env` to **`openai`**, **`anthropic`**, or **`gemini`**, then set the matching credentials. The tutor only returns text; **routing and BKT are unchanged**.

| Provider | Required env vars | Notes |
|----------|-------------------|--------|
| `openai` | `LLM_API_KEY` (or `OPENAI_API_KEY`), optional `LLM_BASE_URL`, `LLM_MODEL` | OpenAI or any OpenAI-compatible `POST /v1/chat/completions` with Bearer auth |
| `anthropic` | `ANTHROPIC_API_KEY`, optional `ANTHROPIC_MODEL`, `ANTHROPIC_API_URL`, `ANTHROPIC_VERSION` | [Claude Messages API](https://docs.anthropic.com/en/api/messages) |
| `gemini` | `GEMINI_API_KEY`, optional `GEMINI_MODEL`, `GEMINI_API_BASE_URL` | [Gemini generateContent](https://ai.google.dev/api/generate-content) |

Also: `LLM_TIMEOUT_SEC` (optional). Use the **AI tutor** panel on Map and Practice after configuration.

## References

- Corbett & Anderson (1995) — Bayesian Knowledge Tracing
- VanLehn (2006) — Outer/Inner loop in ITS
- Brusilovsky (2001) — Adaptive Hypermedia
- Piech et al. (2015) — Deep Knowledge Tracing

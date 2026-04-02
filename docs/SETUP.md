# Setup Guide

Two ways to run the app — pick the one that suits you.

---

## Option A — Docker (recommended)

Starts everything: PostgreSQL, FastAPI backend, Next.js frontend, and pgAdmin.

**Requirements:** [Docker](https://docs.docker.com/get-docker/) with Compose v2.

```bash
docker compose up --build
```

| Service | URL |
|---------|-----|
| Web app | http://localhost:3000 |
| API + Swagger | http://localhost:8000/docs |
| pgAdmin | http://localhost:5050 — `admin@admin.com` / `admin` |
| PostgreSQL (direct) | `localhost:5434` — `postgres` / `postgres` / `cs_learning` |

The backend container runs Alembic migrations and seeds the database automatically on first start.

---

## Option B — Local processes

**Requirements:** Docker (for Postgres only), Python 3.12+, Node.js 20+, npm.

### 1. Start the database

```bash
docker compose up -d db
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
```

### 3. Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Open http://localhost:3000.

---

## AI Tutor (optional)

The tutor panel uses Claude by default. It's optional — routing and BKT work without it.

1. Copy `backend/.env.example` → `backend/.env` if you haven't already.
2. Get an API key from [Anthropic Console](https://console.anthropic.com/).
3. Add it to `backend/.env`:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```
4. Restart the backend.

Other supported providers:

| Provider | Required env vars |
|----------|-------------------|
| `anthropic` (default) | `ANTHROPIC_API_KEY`, optionally `ANTHROPIC_MODEL` |
| `openai` | `LLM_API_KEY`, optionally `LLM_BASE_URL`, `LLM_MODEL` |
| `gemini` | `GEMINI_API_KEY`, optionally `GEMINI_MODEL` |

Set `LLM_PROVIDER=openai` or `LLM_PROVIDER=gemini` in `.env` to switch providers.

> **Never commit your `.env` file.** It is gitignored by default.

---

## Running tests

```bash
cd backend && pytest tests/ -v
```

---

## BKT parameters

Defaults from Corbett & Anderson (1995). All configurable in `backend/app/services/bkt.py`.

| Parameter | Default | Meaning |
|-----------|---------|---------|
| P(L0) | 0.10 | Prior mastery probability |
| P(T)  | 0.10 | Learning rate per attempt |
| P(G)  | 0.25 | Guess probability |
| P(S)  | 0.10 | Slip probability |
| τ_mastery | 0.95 | Advance threshold |
| τ_low | 0.40 | Reroute threshold |
| k | 3 | Minimum attempts before reroute |

---

## API reference

Base URL: `http://localhost:8000`
Interactive docs: `http://localhost:8000/docs`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/kcs/graph` | Full KC + edge graph |
| `GET` | `/api/v1/items/next` | Next quiz item for learner + KC |
| `POST` | `/api/v1/attempts` | Submit answer → BKT update + decision |
| `GET` | `/api/v1/mastery` | All KC masteries for a learner |
| `POST` | `/api/v1/routes` | Create a learning route toward a goal KC |
| `POST` | `/api/v1/routes/{id}/advance` | Advance after KC mastered |
| `POST` | `/api/v1/routes/{id}/reroute` | Backtrack to prerequisite |
| `DELETE` | `/api/v1/mastery/{id}` | Reset learner progress (demo) |
| `POST` | `/api/v1/tutor/chat` | AI tutor (optional) |

---

## Submission checklist

- [ ] `cd backend && pytest tests/ -v` passes
- [ ] `cd frontend && npm run lint && npm run build` pass
- [ ] End-to-end flow works: landing → goal → map → one practice attempt
- [ ] No secrets or `.env` files committed

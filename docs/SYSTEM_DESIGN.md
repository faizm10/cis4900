# CS Learning Map — Application System Design (As-Built)

This document describes the **implemented** adaptive learning system in this repository. It aligns with the research specification (LaTeX Section 3 in [`docs/research/research-plan.tex`](research/research-plan.tex)) but is grounded in actual modules, APIs, and schema.

## 1. Context

```mermaid
flowchart LR
  subgraph clients [Clients]
    LearnerUI[Learner_UI_Nextjs]
    AdminUI[Admin_UI_Nextjs]
  end
  API[FastAPI_backend]
  DB[(PostgreSQL)]
  LearnerUI -->|HTTPS_JSON| API
  AdminUI -->|HTTPS_JSON| API
  API -->|SQLAlchemy| DB
```

- **Learner UI:** Next.js 14 (App Router), React Flow for the knowledge graph, Zustand for session state (`learner_id`, goal, current KC, route).
- **Backend:** FastAPI, SQLAlchemy 2.x, Alembic migrations, Pydantic v2.
- **Database:** PostgreSQL (connection string via `DATABASE_URL` in [`backend/app/config.py`](../backend/app/config.py)).

## 2. Technology stack

| Layer | Technology |
|--------|------------|
| Frontend | Next.js 14, TypeScript, Tailwind-style utility classes, React Flow |
| Backend | Python 3.12+, FastAPI, Uvicorn |
| ORM / migrations | SQLAlchemy, Alembic |
| DB | PostgreSQL |
| Optional tutor | OpenAI-compatible, Anthropic, or Gemini HTTP APIs (see §8) |

## 3. Backend layout

| Area | Path | Role |
|------|------|------|
| App entry | [`backend/app/main.py`](../backend/app/main.py) | FastAPI app, CORS, router registration |
| Config | [`backend/app/config.py`](../backend/app/config.py) | `DATABASE_URL`, `CORS_ORIGINS`, optional `OPENAI_*` |
| Routers | [`backend/app/routers/`](../backend/app/routers/) | HTTP endpoints (`kcs`, `items`, `attempts`, `mastery`, `routes`, `admin`, `tutor`) |
| Services | [`backend/app/services/`](../backend/app/services/) | `bkt.py` (BKT + thresholds + `decide`), `routing.py` (graph + route + reroute target), `decision.py` (attempt pipeline), `tutor.py` + `llm_clients.py` (optional LLM: openai / anthropic / gemini) |
| Models | [`backend/app/models/`](../backend/app/models/) | SQLAlchemy entities |

## 4. Data model (PostgreSQL)

| Table | Key columns | Purpose |
|-------|-------------|---------|
| `kc` | `kc_id`, `name`, `description`, `p_l0`, `p_t`, `p_g`, `p_s`, `created_ts` | Knowledge component + per-KC BKT parameters |
| `prereq_edge` | `edge_id`, `from_kc_id`, `to_kc_id` | Prerequisite: `from` must be mastered before `to` |
| `item` | `item_id`, `kc_id`, `prompt`, `type`, `choices`, `answer`, `difficulty` | Assessment item (v1: one KC per item) |
| `attempt` | `attempt_id`, `learner_id`, `item_id`, `kc_id`, `correctness`, `timestamp`, `metadata` | Observed evidence |
| `mastery` | `mastery_id`, `learner_id`, `kc_id`, `p_mastery`, `attempt_count`, `updated_ts` | Student model state per learner–KC |
| `route` | `route_id`, `learner_id`, `goal_kc_id`, `ordered_kc_ids` (JSONB), `next_kc_id`, timestamps | Cached learning path |

## 5. Policy parameters (BKT + outer loop)

Defined in [`backend/app/services/bkt.py`](../backend/app/services/bkt.py):

| Symbol | Constant | Value | Meaning |
|--------|----------|-------|---------|
| τ_mastery | `TAU_MASTERY` | 0.95 | KC treated as mastered → `advance` |
| τ_low | `TAU_LOW` | 0.40 | Below this after enough attempts → `reroute` eligible |
| k | `K_REROUTE` | 3 | Minimum attempts before reroute |
| P(L₀), P(T), P(G), P(S) | KC columns | defaults 0.1, 0.1, 0.25, 0.1 | Per-KC overrides in DB |

Routing uses the same τ_mastery to decide which nodes are “mastered” for graph purposes ([`routing.py`](../backend/app/services/routing.py)).

## 6. Core runtime flows

### 6.1 Create or refresh route

1. Client: `POST /api/v1/routes` with `{ learner_id, goal_kc_id }`.
2. Server loads mastery map and prerequisite graph, runs `compute_route` ([`routing.py`](../backend/app/services/routing.py)).
3. Persists/updates `route` row; `next_kc_id` = first KC in ordered list.

### 6.2 Practice loop (attempt → BKT → decision)

1. Client: `GET /api/v1/items/next?learner_id=&kc_id=` — picks next item (avoids last 3 seen for variety).
2. Client: `POST /api/v1/attempts` with `{ learner_id, item_id, kc_id, response }`.
3. [`process_attempt`](../backend/app/services/decision.py): validates item/KC, scores MC answer, runs `bkt_update`, `decide`, persists `attempt` + `mastery`.
4. Response includes `decision` (`advance` | `remediate` | `reroute`), mastery before/after, feedback, and human-readable `decision_rationale`.
5. If `advance`: client calls `POST /api/v1/routes/{learner_id}/advance`.
6. If `reroute`: client calls `POST /api/v1/routes/{learner_id}/reroute` ([`find_reroute_target`](../backend/app/services/routing.py)).

### 6.3 Reroute semantics

`reroute` recomputes the ordered route from current mastery, then sets `next_kc_id` to the nearest unmastered predecessor on that path (or first KC on the route).

## 7. HTTP API map (v1)

Prefix: `/api/v1` (see Swagger at `/docs`).

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/kcs`, `/kcs/graph`, `/kcs/{id}` | List KCs, graph for map, single KC |
| GET/POST/PUT/DELETE | `/kcs`, `/kcs/{id}` | Admin KC CRUD (as implemented) |
| GET/POST/DELETE | `/edges`, `/edges/{id}` | Prerequisite edges |
| GET | `/items`, `/items/next`, `/items/{id}` | Item bank + next item |
| POST | `/attempts` | Submit answer → BKT + decision |
| GET | `/attempts` | Attempt history |
| GET/DELETE | `/mastery`, `/mastery/...` | Mastery snapshot + reset |
| POST/GET | `/routes`, `/routes/{learner_id}` | Create/get route |
| POST | `/routes/{learner_id}/advance`, `.../reroute` | After attempt decisions |
| GET/POST | `/admin/stats`, `/admin/seed` | Admin utilities |
| POST | `/tutor/chat` | Optional explanation tutor (requires API key) |

## 8. Optional AI tutor (explanation-only)

- **Config:** `LLM_PROVIDER` = `openai` | `anthropic` | `gemini`. For **openai**: `LLM_API_KEY`, optional `LLM_BASE_URL` / `LLM_MODEL` (OpenAI-compatible chat completions). For **anthropic**: `ANTHROPIC_API_KEY`, optional `ANTHROPIC_MODEL`, `ANTHROPIC_API_URL`, `ANTHROPIC_VERSION`. For **gemini**: `GEMINI_API_KEY`, optional `GEMINI_MODEL`, `GEMINI_API_BASE_URL`. Implementation: [`backend/app/services/llm_clients.py`](../backend/app/services/llm_clients.py).
- **Behavior:** `POST /api/v1/tutor/chat` returns natural-language help. **Sequencing and mastery remain authoritative** in BKT + routing; the model does not change `next_kc_id` or DB state.
- **Code:** [`backend/app/services/tutor.py`](../backend/app/services/tutor.py), [`backend/app/routers/tutor.py`](../backend/app/routers/tutor.py).

### 8.1 Analysis: which LLM fits this application?

There is no single “best” model for every deployment; the right choice depends on **budget, latency expectations, compliance, and how much you trust the model on CS facts** without extra guardrails. This subsection relates generic LLM trade-offs to **how this repo actually uses** the tutor (as-built).

#### 8.1.1 What the tutor workload is (as implemented)

From [`tutor.py`](../backend/app/services/tutor.py) and [`llm_clients.py`](../backend/app/services/llm_clients.py):

| Aspect | Implication for model choice |
|--------|-------------------------------|
| **Task shape** | Single-turn (system + user) **chat**: explanations, hints, and short “what to focus on” guidance. No tool calling, no retrieval, no multi-step agent loop. |
| **Grounding** | The model sees a **small structured context block**: goal KC name, ordered route as names, **next topic chosen by the app**, optional current KC and **BKT mastery estimate** `P(L)`. It does **not** see full item text unless the learner pastes it in `message`. |
| **Safety / policy** | System prompt instructs: stay concise, **do not tell the learner to skip app ordering** or claim the model changed their path. Quality depends on **instruction following**, not raw trivia score. |
| **Length & sampling** | OpenAI-compatible path: `max_tokens` 500, `temperature` 0.5. Anthropic/Gemini: up to 1024 output tokens, temperature 0.5. Favors **short, focused** answers. |
| **Timeout** | `LLM_TIMEOUT_SEC` (default 60s in settings) bounds httpx; perceived UX still favors models/endpoints with **low tail latency**. |
| **Domain** | Seed content is **intro CS with Python** (variables through recursion). Models often do well here, but **code and conceptual errors** still occur—especially in edge explanations. |

So the “best” LLM here is primarily a **good short-form CS tutor that follows the system contract**, not necessarily the strongest model on long reasoning or competition math.

#### 8.1.2 Dimensions to score candidates against

1. **Instruction following under a fixed system prompt** — Will it consistently avoid contradicting the app’s route and “next topic”? Failures here undermine trust in the whole adaptive UI even though BKT is unchanged.
2. **Pedagogical clarity (intro CS, Python)** — Clear definitions, small examples, appropriate difficulty; avoids overwhelming the learner in one bubble.
3. **Factual reliability** — Risk of subtle bugs in sample code or wrong statements about Python semantics. Smaller/cheaper models tend to need **more content QA** on your prompts and KC descriptions.
4. **Latency and cost** — Tutor is optional but **interactive**; cold starts and slow regions hurt UX. Cost scales with sessions × calls; cap on output tokens already limits spend per call.
5. **Operability** — Fits your stack: this codebase supports **OpenAI-compatible** servers (including many gateways and self-hosted endpoints), **Anthropic Messages API**, and **Gemini generateContent**.
6. **Privacy / data residency** — If learner IDs or pasted code must not leave a jurisdiction, prefer **enterprise endpoints** or **self-hosted** OpenAI-compatible inference behind `LLM_BASE_URL`.

#### 8.1.3 Recommendations by scenario

These are **pragmatic defaults**, not ranked benchmarks. Re-evaluate when you change prompts, add RAG over course materials, or expose the model to full quiz items server-side.

| Priority | Suggested direction | Rationale |
|----------|--------------------|-----------|
| **Balanced quality for a research or pilot demo** | **Anthropic Claude** (e.g. a current **Sonnet**-class model via `LLM_PROVIDER=anthropic`) | Typically strong at **nuanced, careful** explanations and following “do not override the app” style constraints; good fit for tutoring tone. Usually **higher cost** than small models. |
| **Low cost + acceptable quality for class-scale use** | **OpenAI** `gpt-4o-mini` or similar small multimodal chat model via `LLM_PROVIDER=openai`, or **Gemini** Flash-class via `gemini` | **Fast and economical** for short answers; adequate for many intro-CS hints. Plan for **spot checks** on explanations and code snippets. |
| **Maximum reasoning depth (occasional deep dives)** | **OpenAI** larger GPT-4.x / 4o-class or **Anthropic** Opus-class (if budget allows) | Useful if learners paste longer code or errors; often **slower and pricier**; still bounded by your `max_tokens` unless you raise limits in code. |
| **On-prem or no third-party API** | **OpenAI-compatible** local or VPC endpoint (`LLM_BASE_URL` + `LLM_MODEL`) | Meets **privacy** and fixed-cost goals; you own **ops, capacity, and model refresh**. Quality varies by open-weight model and quantization; **instruction following** may be weaker than frontier APIs—test against your system prompt. |
| **Already standardized on Google Cloud** | **Gemini** with `GEMINI_API_KEY` | Straightforward integration path; compare **latency** from your region and **policy** on academic use. |

**Summary:** For **this** architecture—**explanation-only**, **short outputs**, **strong separation** from routing—prioritize **instruction following + CS teaching quality** first, then **latency/cost**. If you must pick one default without other constraints: **Claude Sonnet-class (Anthropic)** is the most natural fit for **pilot quality**; **GPT-4o-mini or Gemini Flash-class** is the most natural fit for **high-volume economy**.

#### 8.1.4 Validation specific to this project

- **Red-team the system prompt:** Ask the model to “skip to recursion” or “ignore the app’s next topic” and verify refusals or safe redirects.
- **Content QA:** For each KC, sample N tutor replies (with empty vs. specific learner questions) and have a human label **correctness** and **alignment** with prerequisites.
- **Regression when swapping models:** Changing `LLM_MODEL` or provider can change tone and length; adjust `max_tokens` / temperature in [`llm_clients.py`](../backend/app/services/llm_clients.py) if needed.

#### 8.1.5 Non-goals (v1)

The tutor does **not** select items, update mastery, or modify routes. Therefore you **do not** need models with the strongest **tool-use** or **long-context** capabilities for v1 unless you extend the product (e.g. retrieval over textbooks, automatic misconception detection writing to the DB). Those extensions would change the analysis.

## 9. Frontend routes

| Path | Purpose |
|------|---------|
| `/` | Landing — learner id (demo identity) |
| `/goal` | Choose goal KC; creates route |
| `/map` | React Flow graph, route chips, legend, optional tutor panel |
| `/activity` | Next item, submit, mastery bar, decision modals, rationale, tutor |
| `/progress` | Mastery + attempt history |
| `/admin` | KC / item / edge management |

Global navigation: [`frontend/src/components/shared/NavBar.tsx`](../frontend/src/components/shared/NavBar.tsx).

## 10. Mapping: LaTeX design (§3) → implementation

| Research spec (§3) | Implementation |
|--------------------|----------------|
| 3.1 Architecture overview | Next.js ↔ FastAPI ↔ Postgres; services as above |
| 3.2 End-to-end flow | **Diagnostic phase:** not implemented as a separate screen; mastery starts from KC priors and updates on first attempts. Warm-up quiz could reuse the same APIs. |
| 3.3 Core data model | Tables match entities in §4 |
| 3.4 BKT update service | [`bkt.py`](../backend/app/services/bkt.py), invoked from [`decision.py`](../backend/app/services/decision.py) |
| 3.5 Routing + rerouting | [`routing.py`](../backend/app/services/routing.py), [`routes.py`](../backend/app/routers/routes.py) |
| 3.6 Learner UI | Map, route strip, activity, progress; plus **why-next** rationale on route payload and post-attempt text |
| 3.7 Deployment | Per [`README.md`](../README.md) — static/SSR frontend, API process, managed Postgres |

## 11. UX notes (spec vs. built)

- **Strengths:** Map metaphor, visible route, mastery visualization, advance/reroute modals, plain-language policy rationale (API + UI).
- **Gap:** Standalone diagnostic before routing (paper §3.2) is **not** a separate flow; consider documenting as future work or aligning the paper with v1.

---

*For build instructions for the research PDF, see [`docs/research/README.md`](research/README.md).*

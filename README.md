# CS Learning Map

> **"Google Maps for Learning"** — an adaptive CS education platform that builds a personalized path through prerequisite concepts using Bayesian Knowledge Tracing.

---

## Demo

<video src="https://github.com/user-attachments/assets/d7d55c6c-8e0e-4c0a-b53b-cbbacec1bebe" controls width="100%"></video>

### What it does

A learner picks a goal (e.g. *Recursion*), and the system builds a personalised route through any prerequisite KCs they haven't mastered yet. At each step, a quiz question is served, mastery is updated via BKT, and the system decides whether to advance, remediate, or reroute — all explained to the learner in plain language.

---

## How it works

**Bayesian Knowledge Tracing (BKT)** estimates the probability a learner has mastered each Knowledge Component (KC) after every attempt, accounting for guessing and slipping.

**Prerequisite Graph** — a DAG of CS concepts. The routing engine uses backward BFS + topological sort to find the shortest prerequisite path to a goal.

**Decision Policy** — after each answer the system picks one of three actions:

| Decision | Trigger |
|----------|---------|
| **Advance** | P(mastery) ≥ 0.95 |
| **Remediate** | Keep practicing current KC |
| **Reroute** | P(mastery) < 0.40 after ≥ 3 attempts → fall back to prerequisite |

**Optional AI Tutor** — a Claude / OpenAI / Gemini-backed tutor panel on Map and Practice screens. The tutor is text-only; it never affects routing or BKT.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 (App Router), React Flow, Zustand, Tailwind CSS |
| Backend | FastAPI, SQLAlchemy, Alembic |
| Database | PostgreSQL |
| Infra | Docker Compose |

## Running it yourself

See **[`docs/SETUP.md`](docs/SETUP.md)** for step-by-step setup instructions (Docker or local).

# Streckbase V3 — Backend

Python rewrite of `streckbase_v2` (Node/Express/TypeScript) using FastAPI + SQLModel, managed with [uv](https://docs.astral.sh/uv/).

## Tech Stack

- **Python** 3.13 (managed by uv)
- **FastAPI** — web framework
- **SQLModel** — ORM over the existing MySQL schema
- **PyMySQL** — MySQL driver
- **uvicorn** — ASGI server (port 8080, same as v2)

## Layout

```
src/streckbase/
├── main.py           # app factory + uvicorn entry
├── api/              # routers (thin HTTP layer)
├── services/         # business logic
├── repositories/     # DB access
├── models/           # SQLModel table models
├── schemas/          # request/response DTOs
└── core/             # config, db engine
```

## Local Dev Setup

1. Copy `.env.example` to `.env` and fill in the database password
   (same keys as v2 — an existing v2 `.env` works as-is).
2. `uv sync`
3. `uv run serve` — starts on http://localhost:8080 with auto-reload

API docs at http://localhost:8080/docs once running.


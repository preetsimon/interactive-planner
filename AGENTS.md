# AGENTS.md

## What this is

Personal Operating System (POS) — a rules-enforcing time management system, not a passive calendar. The spec at `planner-spec.md` is the single source of truth for architecture, data model, business rules, and implementation order.

## Stack (do not substitute)

- **Backend:** Python 3.10+, FastAPI, SQLAlchemy 2.0 (async), Pydantic, SQLite (dev) / PostgreSQL (prod)
- **Frontend:** React + TypeScript + Tailwind CSS v3 (Vite 5, React Router, Lucide icons)
- **Infra:** Docker, Alembic (migrations), APScheduler (background jobs)
- **Testing:** pytest + pytest-asyncio (aiosqlite for test DB), httpx AsyncClient

## Architecture at a glance

```
React SPA (Vite :5173)  ──REST/JSON──▶  FastAPI (:8000)  ──SQLAlchemy 2.0 async──▶  SQLite/PostgreSQL
                                            └── APScheduler (daily/weekly/monthly jobs)
```

Vite proxies `/api` → `localhost:8000` in dev. Five subsystems + two supporting services.

## Project layout

```
frontend/src/
├── components/{charts,layout,ui}   # Reusable UI + SVG charts
├── contexts/                       # ThemeContext (dark mode), AuthContext (JWT)
├── pages/                          # 7 pages: Dashboard, TimeBlocks, Priorities, etc.
├── services/api.ts                 # Typed fetch client, auto-redirect on 401
└── services/types.ts               # TypeScript interfaces matching backend schemas

backend/app/
├── core/          config.py, security.py (JWT + bcrypt)
├── db/            base.py (engine + session), seed.py (categories)
├── models/        9 SQLAlchemy models
├── schemas/       8 Pydantic schemas (XCreate + XRead with UUIDStrMixin)
├── services/      7 business rule modules (priority_gate, block_guard, etc.)
├── api/v1/        6 routers (auth, time_blocks, priorities, cadence, domains, audits)
└── main.py        FastAPI app with CORS + lifespan (auto-create tables + seed)
```

## Running

```bash
# Backend (no Postgres needed — uses SQLite by default)
cd backend && pip3 install -e ".[dev]"  # or install deps directly
PYTHONPATH=. uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && npm install && npm run dev   # → http://localhost:5173

# Tests
cd backend && rm -f test.db && PYTHONPATH=. python3 -m pytest tests/ -v
```

## Non-negotiable business rules

1. **Priority Gate** — hard cap: 1 active TECHNICAL + 1 active LANGUAGE. Second active → HTTP 409. Service layer enforces this; partial unique index added via Alembic for Postgres.
2. **Deadline Enforcer** — at due_date, if not COMPLETED → forced ship (SHIPPED_PARTIAL). Never extend deadlines. No PATCH endpoint on deadlines.
3. **time_blocks logging** — every hour accounted for as a row. Block Guard flags violations but never rejects inserts.

Other rules:
- Background jobs must be **idempotent** (scheduler can double-fire)
- Protected window violations are flagged, not blocked
- Zero logged blocks in a week → MISALIGNED verdict
- Cutting a priority is a first-class success action, not a failure state

## Testing

19 tests across `tests/unit/` and `tests/api/`:

- **Auth:** register, login, duplicate blocked, wrong password, protected route 401
- **Priority Gate:** create, 409 cap, cut-then-add, track independence
- **Cadence:** create quarter, get current, tick phase transition
- **Time Blocks:** create, list, auth required

Run: `cd backend && rm -f test.db && PYTHONPATH=. python3 -m pytest tests/ -v`

E2E: 17-step API flow test (register → login → priorities → cap → cut → cadence → audit) passes against SQLite.

## Frontend conventions

- Dark mode: `dark:` Tailwind classes + `localStorage` persistence + flash prevention in `index.html`
- All API calls go through `src/services/api.ts` — typed, handles 401 auto-redirect
- UUID→string coercion via `UUIDStrMixin` in all Read schemas (handles both dict and ORM input)
- Charts are pure SVG (no chart library) — `BarChart`, `DonutChart`, `SprintRing`, `WeeklyHoursChart`, `QuarterTimeline`

## Gotchas

- `ARRAY` columns use `JSON` type for SQLite compatibility (Postgres uses real arrays via Alembic)
- `passlib` requires `bcrypt==4.1.x` (bcrypt 5.x breaks passlib's internal bug detection)
- The `UniqueConstraint` on priorities is intentionally omitted from the model — partial unique indexes (`WHERE status = 'ACTIVE'`) are Postgres-only and added via Alembic migration
- `seed_categories()` uses Python-side UUID generation (not `gen_random_uuid()`) for cross-DB compatibility

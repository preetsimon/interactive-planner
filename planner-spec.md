# Personal Operating System (POS) — Developer Implementation Specification

**Version:** 1.0
**Purpose:** A personal planner application that enforces a scaling framework (calendar-identity alignment, protected time blocks, priority caps, niche filtering, and cadence loops) for a solo user transitioning careers while working full-time.

**Note on stack choice:** The spec deliberately uses the target user's own learning stack (Python, FastAPI, PostgreSQL, SQLAlchemy, Pydantic, Docker, Pytest, GitHub Actions). Building this app *is* the quarterly sprint project. Do not substitute the stack.

---

## 1. System Overview

The app is a rules-enforcing time management system, not a passive calendar. It has five subsystems mapped to five principles:

| Subsystem | Principle | Behavior |
|---|---|---|
| Identity Auditor | Calendar = identity | Weekly comparison of logged hours vs. stated goals; flags mismatch |
| Block Guard | Blank space | Daily protected time window; blocks reactive categories; logs violations |
| Priority Gate | Subtraction | Hard cap: 1 active technical priority + 1 language priority; rejects additions until something is removed |
| Niche Filter | Zone of genius | Scores job-search domains against core assets; enforces daily work cutoff boundary |
| Cadence Engine | Chaos to cadence | Nested annual/quarterly/monthly/weekly loop with phases (Rest → Review → 8-week Sprint) and immovable deadlines |

Supporting services: **Time Audit** (weekly proactive/reactive ratio report) and **Deadline Enforcer** (Parkinson's Law — scope cuts, never date extensions).

---

## 2. Architecture

```
┌─────────────────────────────────────────────┐
│  Client (any: web SPA, mobile, CLI)         │
└──────────────────┬──────────────────────────┘
                   │ REST / JSON
┌──────────────────▼──────────────────────────┐
│  FastAPI application                        │
│  ├── /api/v1 routers                        │
│  ├── Pydantic schemas (request/response)    │
│  ├── Service layer (business rules)         │
│  └── Auth middleware (JWT, single user OK)  │
└──────────────────┬──────────────────────────┘
                   │ SQLAlchemy 2.0 (async)
┌──────────────────▼──────────────────────────┐
│  PostgreSQL 16                              │
└─────────────────────────────────────────────┘

Background jobs: APScheduler (in-process) or a cron container.
Runs: daily block-guard check, weekly audits, monthly checkpoints,
quarterly phase transitions.
```

**Project layout**

```
pos/
├── app/
│   ├── main.py                 # FastAPI app factory
│   ├── core/
│   │   ├── config.py           # Pydantic Settings (env vars)
│   │   ├── security.py         # JWT creation/validation, password hash
│   │   └── scheduler.py        # APScheduler job registration
│   ├── db/
│   │   ├── base.py             # DeclarativeBase, session factory
│   │   └── migrations/         # Alembic
│   ├── models/                 # SQLAlchemy ORM models
│   ├── schemas/                # Pydantic models
│   ├── services/               # Business logic (one module per subsystem)
│   │   ├── identity_audit.py
│   │   ├── block_guard.py
│   │   ├── priority_gate.py
│   │   ├── niche_filter.py
│   │   ├── cadence.py
│   │   ├── deadline.py
│   │   └── time_audit.py
│   ├── api/
│   │   └── v1/
│   │       ├── router.py
│   │       ├── time_blocks.py
│   │       ├── priorities.py
│   │       ├── audits.py
│   │       ├── cadence.py
│   │       ├── domains.py
│   │       └── auth.py
│   └── events/                 # audit_log writer
├── tests/
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .github/workflows/ci.yml
```

---

## 3. Data Model

All tables include `id UUID PK`, `created_at`, `updated_at`. Single-user system, but include `user_id` on every table anyway — costs nothing now, enables multi-user later, and matches production norms (the point of this project is production-quality habits).

### 3.1 `users`
| Column | Type | Notes |
|---|---|---|
| email | text unique | |
| password_hash | text | bcrypt/argon2 |
| stated_goal | text | e.g. "Backend engineer + professional French" |
| work_cutoff_time | time | e.g. 21:00 — boundary enforcement |
| weekly_goal_hours_threshold | int | default 10 — identity audit threshold |

### 3.2 `categories` (seeded enum-like table)
Seed rows: `JOB`, `CODING_PROACTIVE`, `CODING_REACTIVE`, `FRENCH_OUTPUT`, `FRENCH_PASSIVE`, `JOB_SEARCH_NOISE`, `PASSIVE_CONSUMPTION`, `REST`, `LIFE`.

| Column | Type | Notes |
|---|---|---|
| name | text unique | |
| classification | enum(`PROACTIVE`,`REACTIVE`,`NEUTRAL`) | drives audit ratio |
| goal_aligned | bool | drives identity audit numerator |

Classification seed: `CODING_PROACTIVE`, `FRENCH_OUTPUT` → PROACTIVE + goal_aligned. `JOB_SEARCH_NOISE`, `PASSIVE_CONSUMPTION`, `CODING_REACTIVE`, `FRENCH_PASSIVE` → REACTIVE. `JOB`, `REST`, `LIFE` → NEUTRAL.

### 3.3 `time_blocks`
The core log. Every hour the user accounts for becomes a row.

| Column | Type | Notes |
|---|---|---|
| user_id | FK | |
| category_id | FK | |
| start_at | timestamptz | |
| end_at | timestamptz | CHECK end_at > start_at |
| notes | text nullable | |
| violates_protected_window | bool | set by Block Guard on insert |
| violates_cutoff | bool | set by boundary check on insert |

Index: `(user_id, start_at)`.

### 3.4 `protected_windows`
| Column | Type | Notes |
|---|---|---|
| user_id | FK | |
| start_time | time | e.g. 06:00 |
| end_time | time | e.g. 09:00 |
| days_of_week | int[] | 1–7 |
| allowed_category_ids | UUID[] | typically CODING_PROACTIVE, FRENCH_OUTPUT |
| active | bool | |

### 3.5 `priorities`
| Column | Type | Notes |
|---|---|---|
| user_id | FK | |
| title | text | |
| track | enum(`TECHNICAL`,`LANGUAGE`) | |
| status | enum(`ACTIVE`,`COMPLETED`,`CUT`,`REJECTED`) | |
| quarter_id | FK nullable | |
| definition_of_done | text NOT NULL | forces concrete outcomes ("ship API with auth + tests + CI") — no vague "learn X" |

**DB-level constraint** (belt and suspenders on top of service logic):
```sql
CREATE UNIQUE INDEX one_active_per_track
ON priorities (user_id, track)
WHERE status = 'ACTIVE';
```

### 3.6 `quarters`
| Column | Type | Notes |
|---|---|---|
| user_id | FK | |
| year, quarter_num | int | unique together per user |
| theme | text | |
| phase | enum(`REST`,`REVIEW`,`SPRINT`,`CLOSED`) | |
| rest_start / review_start / sprint_start / sprint_end | date | sprint_end = sprint_start + 8 weeks; **immutable after creation** |

### 3.7 `deadlines`
| Column | Type | Notes |
|---|---|---|
| priority_id | FK | |
| due_date | date | **no UPDATE allowed** (enforce in service layer + DB trigger or omit update endpoint entirely) |
| status | enum(`OPEN`,`SHIPPED_COMPLETE`,`SHIPPED_PARTIAL`) | partial = forced ship at deadline |
| scope_cuts | jsonb | log of scope reductions made at monthly checkpoints |

### 3.8 `target_domains`
| Column | Type | Notes |
|---|---|---|
| user_id | FK | |
| name | text | e.g. "LIMS", "healthcare tech" |
| required_assets | text[] | tags the domain values |
| score | numeric | computed: overlap with user core assets |
| status | enum(`ACTIVE`,`CUT`) | below-threshold domains auto-cut |

### 3.9 `core_assets` (seeded per user)
`physics`, `lab_qc`, `regulated_procedures`, `chemical_analysis`, `backend_eng`, `french` — text tags with optional weight.

### 3.10 `audit_reports`
| Column | Type | Notes |
|---|---|---|
| user_id | FK | |
| type | enum(`TIME_AUDIT`,`IDENTITY_AUDIT`,`MONTHLY_CHECKPOINT`,`QUARTERLY_REVIEW`) | |
| period_start / period_end | date | |
| payload | jsonb | full computed report |
| verdict | enum(`ALIGNED`,`MISALIGNED`,`ON_TRACK`,`BEHIND`) | |

### 3.11 `audit_log` (event sourcing lite)
Append-only: every rejection, violation, forced ship, scope cut. `(user_id, event_type, entity_type, entity_id, detail jsonb, occurred_at)`. This table is the app's honesty mechanism — nothing gets silently ignored.

---

## 4. Business Rules (Service Layer)

Implement each as a pure-ish service function taking a DB session. All rules write to `audit_log`.

### 4.1 Identity Audit — `identity_audit.run(user_id, week_start)`
1. Sum `time_blocks` hours for the trailing 7 days, grouped by category.
2. `goal_hours = Σ hours WHERE category.goal_aligned = true`.
3. If `goal_hours < user.weekly_goal_hours_threshold` → verdict `MISALIGNED`, persist report with breakdown, raise notification.
4. Always persist the report even when aligned (trend data).

**Edge cases:** weeks with zero logged blocks → verdict `MISALIGNED` with reason `NO_DATA` (unlogged time is presumed reactive — the audit must not be skippable by simply not logging).

### 4.2 Block Guard — runs on `time_blocks` insert + daily job
On insert:
1. Find active `protected_windows` overlapping `[start_at, end_at]` for that weekday.
2. If overlap exists and `category_id ∉ allowed_category_ids` → set `violates_protected_window = true`, write `audit_log` event `PROTECTED_WINDOW_VIOLATION`. **Do not reject the insert** — the log must reflect reality; the system flags, the review phase confronts.
3. If block start or end falls after `user.work_cutoff_time` and category is goal-aligned work → set `violates_cutoff = true`, log `CUTOFF_VIOLATION`. (Boundary exists to prevent burnout, not to prevent honesty.)

Daily job (end of day): if the protected window for that day contains **zero** proactive blocks, log `PROTECTED_WINDOW_UNUSED`. An empty protected window is as much a failure as a violated one.

### 4.3 Priority Gate — `priority_gate.add(user_id, payload)`
1. Count `ACTIVE` priorities on the requested track.
2. If ≥ 1 → **reject** with HTTP 409 and body:
   ```json
   {
     "error": "PRIORITY_CAP",
     "message": "1 active TECHNICAL priority allowed. Cut or complete the existing one first.",
     "blocking_priority": { "id": "...", "title": "..." }
   }
   ```
   Log `PRIORITY_REJECTED`.
3. Validate `definition_of_done` is non-empty and contains a verifiable artifact (minimum: length check + required at API level; do not attempt NLP validation).
4. On first-ever run / onboarding: if the user imports > 1 priority per track, force an interactive reduction flow — API returns the full list and requires explicit `CUT` decisions before any becomes `ACTIVE`.

`priority_gate.cut(priority_id)` → status `CUT`, log `PRIORITY_CUT`. Cutting is a first-class success action in the UI, not a failure state.

### 4.4 Niche Filter — `niche_filter.score_all(user_id)`
1. For each `target_domain`: `score = |required_assets ∩ core_assets| / |required_assets|` (weighted if weights present).
2. Domains with `score < 0.5` (configurable) → status `CUT`, log `DOMAIN_CUT`.
3. Return active domains sorted descending. This list feeds any job-search views.

Re-run whenever `core_assets` change (e.g., French proficiency milestone added).

### 4.5 Cadence Engine — `cadence.tick()` (daily job)
State machine on the current quarter:

```
CLOSED → (quarter start) → REST → (rest_end) → REVIEW → (review_end) → SPRINT → (sprint_end) → CLOSED
```

Transition actions:
- **→ REST:** notify; suppress sprint nags; goal-aligned logging still allowed but not demanded.
- **→ REVIEW:** auto-generate `QUARTERLY_REVIEW` report: last quarter's priority outcome, aggregate time audit, violation counts, domain scores. Block sprint start until the user has (a) confirmed exactly 1+1 active priorities, (b) set the sprint theme, (c) a `deadline` row exists = sprint_end.
- **→ SPRINT:** lock theme and deadline. Weeks numbered 1–8.
- **→ CLOSED:** invoke Deadline Enforcer (4.6); auto-create next quarter in REST phase.

Monthly job (1st of month, during SPRINT only): compute expected vs. actual progress proxy = goal-aligned hours to date vs. pro-rata plan. If behind → report `BEHIND` with required action `CUT_SCOPE`, and require the user to append an entry to `deadlines.scope_cuts` before the report can be acknowledged. **The API must not offer any endpoint to move `due_date`.**

### 4.6 Deadline Enforcer — `deadline.enforce(deadline_id)` (runs at due_date)
1. If priority not `COMPLETED` → set deadline `SHIPPED_PARTIAL`, priority `COMPLETED` (forced), log `FORCED_SHIP` with the state description the user supplies (or `NONE_PROVIDED`).
2. Feed outcome into next quarter's REVIEW payload.
3. Never extend. No exceptions in code paths. If the user wants more time, that is a *new* priority in the *next* quarter — which forces re-justification against the cap.

### 4.7 Time Audit — `time_audit.run(user_id, week_start)` (weekly job)
1. `proactive = Σ hours WHERE classification = PROACTIVE`
2. `reactive = Σ hours WHERE classification = REACTIVE`
3. `ratio = proactive / max(reactive, ε)`
4. `ratio < 1.0` → alert `REACTIVE_DOMINANT`.
5. Persist full category breakdown, ratio trend vs. previous 4 weeks.

**Execution order on first launch (onboarding):** time_audit (seed week of manual logging first) → identity_audit → priority force-reduction → niche_filter → activate block guard + cadence. Do not let the user skip to sprint planning without one week of honest logging — the audit determines which principle is actually the bottleneck.

---

## 5. API Design (`/api/v1`)

Auth: `POST /auth/register`, `POST /auth/login` → JWT bearer. All routes below require auth.

### Time Blocks
| Method | Path | Notes |
|---|---|---|
| POST | `/time-blocks` | body: category_id, start_at, end_at, notes. Returns block incl. violation flags. |
| GET | `/time-blocks?from=&to=` | paginated |
| DELETE | `/time-blocks/{id}` | logs `BLOCK_DELETED` to audit_log (deletions are visible) |

### Priorities
| Method | Path | Notes |
|---|---|---|
| POST | `/priorities` | 409 on cap violation (see 4.3) |
| GET | `/priorities?status=` | |
| POST | `/priorities/{id}/cut` | |
| POST | `/priorities/{id}/complete` | requires deadline status transition |

### Cadence
| Method | Path | Notes |
|---|---|---|
| GET | `/cadence/current` | quarter, phase, sprint week, days to deadline |
| POST | `/cadence/quarters` | create next quarter (theme optional until REVIEW) |
| POST | `/cadence/review/confirm` | gate to enter SPRINT; validates 1+1 priorities + deadline exist |
| POST | `/deadlines/{id}/scope-cuts` | append-only |

*(No PATCH on deadlines. Intentional.)*

### Audits & Reports
| Method | Path | Notes |
|---|---|---|
| GET | `/reports?type=&from=&to=` | |
| POST | `/reports/{id}/acknowledge` | BEHIND reports require a scope_cut first |
| GET | `/audit-log?from=&to=` | read-only event stream |

### Domains
| Method | Path | Notes |
|---|---|---|
| GET | `/domains` | sorted by score |
| POST | `/domains` | auto-scored on create |
| POST | `/domains/rescore` | after core_assets change |
| PUT | `/core-assets` | replace set |

### Protected Windows
Standard CRUD at `/protected-windows`.

**Pydantic conventions:** separate `XCreate`, `XUpdate`, `XRead` schemas; `model_config = ConfigDict(from_attributes=True)` on reads; enums as `str, Enum`; all datetimes timezone-aware (`AwareDatetime`), reject naive datetimes at validation.

---

## 6. Background Jobs

| Job | Schedule | Function |
|---|---|---|
| daily_block_guard_check | 23:55 daily | flag unused protected windows |
| cadence_tick | 00:05 daily | phase transitions, deadline enforcement |
| weekly_audits | Mon 06:00 | time_audit + identity_audit |
| monthly_checkpoint | 1st 06:00 | sprint progress check |

Use APScheduler with the SQLAlchemy job store (survives restarts), or a separate cron container calling internal endpoints with a service token. Jobs must be **idempotent** (guard with "report already exists for period" checks) — assume the scheduler can double-fire.

---

## 7. Configuration

`app/core/config.py` via `pydantic-settings`:

```python
class Settings(BaseSettings):
    database_url: PostgresDsn
    jwt_secret: SecretStr
    jwt_expire_minutes: int = 60 * 24
    weekly_goal_hours_default: int = 10
    domain_score_threshold: float = 0.5
    sprint_length_weeks: int = 8
    rest_phase_days: int = 7
    review_phase_days: int = 7
    model_config = SettingsConfigDict(env_file=".env")
```

---

## 8. Testing Strategy (Pytest)

Minimum coverage targets — these tests define the product; the rules ARE the app:

1. **Priority Gate:** second ACTIVE technical priority → 409; cut then add → 201; DB unique partial index holds under concurrent inserts (test with two sessions).
2. **Deadline immutability:** no route mutates due_date; `enforce()` at due date on incomplete priority → SHIPPED_PARTIAL + FORCED_SHIP event.
3. **Block Guard:** reactive block inside protected window → flagged, not rejected; empty window at day end → PROTECTED_WINDOW_UNUSED event.
4. **Identity Audit:** below threshold → MISALIGNED; zero blocks → MISALIGNED/NO_DATA.
5. **Cadence state machine:** full REST→REVIEW→SPRINT→CLOSED cycle with time-travel (freezegun); SPRINT entry blocked without 1+1 confirmed priorities.
6. **Time Audit ratio:** proactive/reactive math incl. zero-reactive edge case.
7. **Auth:** protected routes 401 without token.

Structure: `tests/unit/` (services, pure logic, in-memory or transaction-rollback Postgres via testcontainers) and `tests/api/` (httpx AsyncClient against app with test DB). Use `pytest-asyncio`.

---

## 9. Deployment

**docker-compose.yml** (dev): `api` (uvicorn, hot reload), `db` (postgres:16, volume), optional `scheduler` if externalized. **Dockerfile**: multi-stage, `python:3.12-slim`, non-root user, `uvicorn app.main:app`.

**CI (GitHub Actions)** on push/PR:
1. ruff (lint + format check)
2. mypy
3. pytest with Postgres service container
4. docker build
5. (main only) push image to GHCR

Migrations: Alembic, run on container start via entrypoint (`alembic upgrade head`), autogenerate reviewed by hand before commit.

---

## 10. Implementation Order (maps to one 8-week sprint)

| Week | Deliverable |
|---|---|
| 1 | Repo, Docker, CI skeleton, DB models + Alembic, auth |
| 2 | time_blocks CRUD + categories seed |
| 3 | Block Guard + protected windows |
| 4 | Priority Gate (incl. 409 flow + DB constraint) |
| 5 | Time Audit + Identity Audit + reports |
| 6 | Cadence state machine + deadlines + enforcer |
| 7 | Niche Filter, audit_log surface, background jobs wired |
| 8 | Test hardening, docs, forced ship |

Scope-cut order if behind (cut from bottom): Niche Filter → Identity Audit trend history → protected-window flexibility. Never cut: Priority Gate, Deadline Enforcer, time_blocks logging. Those three are the product.

---

## 11. Non-Goals (v1)

- No calendar-provider sync (Google/Outlook) — manual logging is deliberate; friction forces awareness.
- No mobile push — email or in-app notifications only.
- No AI-based time analysis — deterministic rules only; keep it auditable.
- No gamification/streaks — the audit_log is the accountability mechanism.
- No deadline extensions, ever. Not a missing feature. A feature.

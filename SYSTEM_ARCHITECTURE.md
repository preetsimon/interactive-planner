# SYSTEM_ARCHITECTURE.md

> POS — Personal Operating System  
> A rules-enforcing time management system, not a passive calendar.

---

## Table of Contents

1. [Directory Structure](#1-directory-structure)
2. [Technology Stack](#2-technology-stack)
3. [System Architecture Overview](#3-system-architecture-overview)
4. [Backend Architecture](#4-backend-architecture)
5. [Frontend Architecture](#5-frontend-architecture)
6. [Data Model](#6-data-model)
7. [Data Flow](#7-data-flow)
8. [Business Rules Engine](#8-business-rules-engine)
9. [Authentication & Security](#9-authentication--security)
10. [External Dependencies](#10-external-dependencies)
11. [Environment Configuration](#11-environment-configuration)
12. [Docker & Deployment](#12-docker--deployment)
13. [Testing](#13-testing)
14. [Known Limitations](#14-known-limitations)

---

## 1. Directory Structure

```
interactive-planner/
├── AGENTS.md                          # Project rules and conventions
├── planner-spec.md                    # Full product specification
├── docker-compose.yml                 # 3-service orchestration (db, api, frontend)
├── .dockerignore
│
├── backend/
│   ├── pyproject.toml                 # Python project metadata + dev deps
│   ├── requirements.txt               # Pinned runtime deps (Docker builds)
│   ├── Dockerfile                     # Python 3.11-slim, non-root user
│   ├── alembic.ini                    # Alembic config (hardcoded Postgres URL)
│   ├── alembic/
│   │   ├── env.py                     # Async migration runner
│   │   ├── script.py.mako            # Migration template
│   │   └── versions/                  # EMPTY — no migrations exist yet
│   │
│   └── app/
│       ├── main.py                    # FastAPI app entry point (lifespan, CORS, routers)
│       │
│       ├── core/
│       │   ├── config.py              # Pydantic Settings (env-based configuration)
│       │   └── security.py            # JWT creation/validation, bcrypt hashing
│       │
│       ├── db/
│       │   ├── base.py                # Async engine, session factory, get_db dependency
│       │   └── seed.py                # Category seed data (9 fixed categories)
│       │
│       ├── models/                    # 10 SQLAlchemy model files
│       │   ├── user.py                # User
│       │   ├── category.py            # Category (fixed seed data)
│       │   ├── time_block.py          # TimeBlock
│       │   ├── priority.py            # Priority (TECHNICAL / LANGUAGE tracks)
│       │   ├── quarter.py             # Quarter (cadence state machine)
│       │   ├── deadline.py            # Deadline (force-ship at due_date)
│       │   ├── protected_window.py    # ProtectedWindow (time protection rules)
│       │   ├── domain.py              # TargetDomain (niche filter scoring)
│       │   ├── audit.py               # AuditReport + AuditLogEntry
│       │   └── learning.py            # LearningTrack, CurriculumItem, PracticeRoutine, PracticeLog
│       │
│       ├── schemas/                   # 9 Pydantic schema files
│       │   ├── _converters.py         # UUIDStrMixin (UUID→str for both dict and ORM)
│       │   ├── auth.py                # UserRegister, UserLogin, UserRead, Token
│       │   ├── priority.py            # PriorityCreate, PriorityRead, PriorityCapError
│       │   ├── time_block.py          # TimeBlockCreate, TimeBlockRead
│       │   ├── quarter.py             # QuarterCreate, QuarterRead
│       │   ├── deadline.py            # ScopeCutCreate, DeadlineRead
│       │   ├── protected_window.py    # ProtectedWindowCreate, ProtectedWindowRead
│       │   ├── domain.py              # DomainCreate, DomainRead
│       │   ├── audit.py               # AuditReportRead, AuditLogEntryRead
│       │   └── learning.py            # TrackRead, TrackDetailRead, CurriculumItemRead, etc.
│       │
│       ├── services/                  # 9 business logic modules
│       │   ├── priority_gate.py       # Priority cap enforcement (1 TECH + 1 LANG)
│       │   ├── block_guard.py         # Protected window + cutoff violation flagging
│       │   ├── cadence.py             # Quarterly phase state machine
│       │   ├── deadline.py            # Deadline enforcement (force-ship)
│       │   ├── niche_filter.py        # Domain scoring against core assets
│       │   ├── time_audit.py          # Weekly proactive/reactive ratio
│       │   ├── identity_audit.py      # Weekly goal alignment check
│       │   ├── learning.py            # Track seeding + streak computation
│       │   └── learning_curricula.py  # Static curriculum data (Python, French)
│       │
│       ├── api/
│       │   ├── deps.py                # get_current_user dependency (JWT → User)
│       │   └── v1/
│       │       ├── router.py          # Aggregates all sub-routers under /api/v1
│       │       ├── auth.py            # POST /register, POST /login
│       │       ├── priorities.py      # CRUD + cut/complete for priorities
│       │       ├── time_blocks.py     # CRUD for time blocks
│       │       ├── cadence.py         # Quarter management + tick
│       │       ├── domains.py         # Domain scoring + rescore
│       │       ├── audits.py          # Reports + audit log (read-only)
│       │       └── learning.py        # Tracks, items, routines, activity heatmap
│       │
│       └── events/
│           └── __init__.py            # Placeholder (no background jobs implemented)
│
├── frontend/
│   ├── package.json                   # React 18, react-router-dom 7, Tailwind 3, Vite 5
│   ├── vite.config.ts                 # Dev server :5174, proxy /api → :8001
│   ├── tsconfig.json                  # Delegates to tsconfig.app.json + tsconfig.node.json
│   ├── tailwind.config.js             # darkMode: 'class', Inter font
│   ├── postcss.config.js
│   ├── eslint.config.js               # Flat config (ESLint 9)
│   ├── index.html                     # Inter font, dark mode flash prevention
│   ├── Dockerfile                     # Multi-stage: Node 20 build → nginx:alpine serve
│   ├── nginx.conf                     # SPA fallback + /api proxy
│   │
│   └── src/
│       ├── main.tsx                   # React root (StrictMode)
│       ├── App.tsx                    # Provider nesting + routing
│       ├── index.css                  # Tailwind directives, CSS custom properties
│       │
│       ├── contexts/
│       │   ├── AuthContext.tsx         # JWT auth state (login, register, logout)
│       │   └── ThemeContext.tsx        # Dark/light mode toggle + localStorage
│       │
│       ├── services/
│       │   ├── api.ts                 # ApiClient class + typed API modules
│       │   └── types.ts               # TypeScript interfaces matching backend schemas
│       │
│       ├── pages/
│       │   ├── Login.tsx              # Auth form (login + register toggle)
│       │   ├── Dashboard.tsx          # Command center (stats, charts, heatmap)
│       │   ├── TimeBlocks.tsx         # List + delete time blocks
│       │   ├── Priorities.tsx         # CRUD priorities with Priority Gate
│       │   ├── Cadence.tsx            # Quarter creation + phase visualization
│       │   ├── Reports.tsx            # Weekly audit report viewer
│       │   ├── Domains.tsx            # Niche filter — scored target domains
│       │   ├── AuditLog.tsx           # Append-only event stream
│       │   └── Learning.tsx           # Curricula + daily practice tracking
│       │
│       └── components/
│           ├── layout/
│           │   ├── Layout.tsx         # Shell: Sidebar + Header + Outlet
│           │   ├── Sidebar.tsx        # Collapsible nav (8 items)
│           │   └── Header.tsx         # User info, theme toggle, logout
│           │
│           ├── ui/
│           │   └── StatCard.tsx       # Reusable metric card with sparkline
│           │
│           └── charts/               # All pure SVG, no chart libraries
│               ├── ActivityHeatmap.tsx    # GitHub-style contribution grid
│               ├── WeeklyHoursChart.tsx   # Stacked bar (proactive/reactive)
│               ├── CategoryDonut.tsx      # Donut chart with percentages
│               ├── SprintRing.tsx         # Circular progress for sprint week
│               ├── QuarterTimeline.tsx    # Phase step indicator
│               ├── BarChart.tsx           # Generic vertical bars (unused)
│               └── DonutChart.tsx         # Simple donut (unused)
│
└── backend/tests/
    ├── conftest.py                    # Fixtures: db_engine, db_session, client, test_user, auth
    ├── api/
    │   ├── test_auth.py               # 5 tests: register, login, duplicate, wrong password, 401
    │   ├── test_priorities.py         # 4 tests: create, 409 cap, cut, list
    │   ├── test_time_blocks.py        # 3 tests: create, list, auth required
    │   ├── test_cadence.py            # 3 tests: create quarter, get current, tick
    │   └── test_learning.py           # 6 tests: seed, idempotent, detail, toggle, log, ownership
    └── unit/
        ├── test_priority_gate.py      # 4 tests: service-level cap enforcement
        └── test_learning_streak.py    # 7 tests: streak computation (pure function)
```

---

## 2. Technology Stack

### Backend

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Framework | FastAPI | latest | Async REST API |
| ORM | SQLAlchemy | 2.0+ | Async database access (`AsyncSession`) |
| Validation | Pydantic | v2 | Request/response schemas + settings |
| Auth | python-jose | latest | HS256 JWT tokens |
| Passwords | passlib + bcrypt | 4.1.x | Password hashing (bcrypt pinned to 4.1.x for passlib compat) |
| Database (dev) | SQLite + aiosqlite | latest | Zero-config async dev database |
| Database (prod) | PostgreSQL 16 | 16 | Production database with asyncpg driver |
| Migrations | Alembic | latest | Schema version control (configured, no versions yet) |
| Settings | pydantic-settings | latest | `.env` file loading |
| HTTP client | httpx | latest | Async HTTP (used in tests) |
| Linting | Ruff | latest | Fast Python linter (line-length 100) |
| Type checking | mypy | latest | Strict mode with pydantic plugin |
| Testing | pytest + pytest-asyncio | latest | Async test runner with aiosqlite |

### Frontend

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| UI framework | React | 18.3.1 | Component-based UI |
| Language | TypeScript | 5.6.2 | Type safety |
| Bundler | Vite | 5.4.10 | Dev server + production build |
| Routing | react-router-dom | 7.18.1 | Client-side routing with layout routes |
| Styling | Tailwind CSS | 3.4.19 | Utility-first CSS + dark mode |
| Icons | lucide-react | 1.24.0 | Consistent icon set |
| CSS processing | PostCSS + Autoprefixer | latest | Browser compatibility |

### Infrastructure

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Containerization | Docker | Isolated service deployment |
| Orchestration | docker-compose | Multi-service local dev |
| Web server | nginx (Alpine) | Frontend static serving + API proxy |
| Runtime | Python 3.11-slim | Backend runtime base image |
| Runtime | Node 20 Alpine | Frontend build stage |

---

## 3. System Architecture Overview

### High-Level Architecture

```mermaid
graph TB
    subgraph Browser
        SPA[React SPA<br/>Vite :5174]
    end

    subgraph Docker Compose
        subgraph Frontend Container
            NGINX[nginx:alpine<br/>:3000]
        end

        subgraph API Container
            FASTAPI[FastAPI<br/>:8000]
        end

        subgraph Database Container
            PG[PostgreSQL 16<br/>:5432]
        end
    end

    SPA -->|HTTP| NGINX
    NGINX -->|/api proxy| FASTAPI
    NGINX -->|static files| SPA
    FASTAPI -->|SQLAlchemy async| PG
```

### Dev vs Production Data Flow

```mermaid
graph LR
    subgraph Development
        DEV_VITE[Vite Dev Server :5174] -->|proxy /api| DEV_FASTAPI[FastAPI :8001]
        DEV_FASTAPI -->|SQLAlchemy async| DEV_SQLITE[SQLite test.db]
    end

    subgraph Production
        PROD_NGINX[nginx :3000] -->|proxy /api| PROD_FASTAPI[FastAPI :8000]
        PROD_FASTAPI -->|SQLAlchemy async| PROD_PG[PostgreSQL 16 :5432]
    end
```

> **Note**: Dev and production use different ports. Vite runs on :5174 proxying to :8001. Production nginx serves on :3000 proxying to :8000. CORS is configured for `localhost:5173` (mismatch with actual dev port).

### Request Lifecycle

```mermaid
sequenceDiagram
    participant U as Browser
    participant V as Vite/nginx
    participant F as FastAPI Router
    participant S as Service Layer
    participant D as Database

    U->>V: HTTP Request (with JWT Bearer)
    V->>F: Proxy /api/*
    F->>F: CORS check
    F->>F: Parse + validate (Pydantic)
    F->>F: Depends(get_current_user) — decode JWT, fetch User
    F->>S: Call service function
    S->>D: SQLAlchemy query
    D-->>S: Result
    S-->>F: Business logic response
    F-->>V: JSON response (UUIDStrMixin)
    V-->>U: HTTP Response
```

---

## 4. Backend Architecture

### 4.1 Application Entry Point

**File**: `backend/app/main.py`

The FastAPI application uses an async lifespan context manager:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # Dev-only
    seed_categories()  # Idempotent category seeding

    yield

    # Shutdown
    await engine.dispose()
```

- **Startup**: Creates all tables via `Base.metadata.create_all()` (dev convenience, not for production with Alembic). Seeds 9 fixed categories.
- **Shutdown**: Disposes the async engine connection pool.
- **CORS**: Allows `http://localhost:5173` with credentials, all methods and headers.
- **Health check**: Unauthenticated `GET /health` returns `{"status": "ok"}`.
- **Router mounting**: `api_router` at prefix `/api/v1`.

### 4.2 Configuration

**File**: `backend/app/core/config.py`

Uses `pydantic-settings` for env-based configuration:

| Setting | Default | Description |
|---------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://pos:pos@localhost:5432/pos` | Database connection string |
| `JWT_SECRET` | `change-me-in-production` | HS256 signing key (SecretStr) |
| `JWT_EXPIRE_MINUTES` | 1440 (24h) | Token expiration |
| `WEEKLY_GOAL_HOURS_DEFAULT` | 10 | Default weekly goal (unused in code) |
| `DOMAIN_SCORE_THRESHOLD` | 0.5 | Score threshold for niche filter (unused) |
| `SPRINT_LENGTH_WEEKS` | 8 | Sprint duration (unused, hardcoded in cadence) |
| `REST_PHASE_DAYS` | 7 | Rest phase duration (unused, hardcoded) |
| `REVIEW_PHASE_DAYS` | 7 | Review phase duration (unused, hardcoded) |

Loading: `.env` file in backend directory, with `.env.example` as template.

### 4.3 Database Layer

**File**: `backend/app/db/base.py`

- **Engine**: `create_async_engine()` with `pool_pre_ping=True` for stale connection detection.
- **Session factory**: `async_sessionmaker()` with `expire_on_commit=False` (objects remain usable after commit).
- **Dependency**: `get_db()` yields an `AsyncSession` via async context manager.
- **Base**: `DeclarativeBase` subclass for model inheritance.

**File**: `backend/app/db/seed.py`

Seeds 9 fixed categories using raw SQL (`text()`) with named parameters:

| Category | Classification | Goal Aligned |
|----------|---------------|-------------|
| JOB | REACTIVE | No |
| CODING_PROACTIVE | PROACTIVE | Yes |
| CODING_REACTIVE | REACTIVE | No |
| FRENCH_OUTPUT | PROACTIVE | Yes |
| FRENCH_PASSIVE | NEUTRAL | No |
| JOB_SEARCH_NOISE | REACTIVE | No |
| PASSIVE_CONSUMPTION | REACTIVE | No |
| REST | NEUTRAL | No |
| LIFE | NEUTRAL | No |

Idempotency: checks `COUNT(*) FROM categories` before inserting.

### 4.4 API Layer (Routers)

**File**: `backend/app/api/v1/router.py`

Aggregates 7 sub-routers under `/api/v1`:

```
/api/v1/auth/*           — Authentication (unprotected)
/api/v1/priorities/*     — Priority CRUD + cut/complete
/api/v1/time-blocks/*    — Time block CRUD
/api/v1/cadence/*        — Quarter management + tick
/api/v1/domains/*        — Domain scoring + rescore
/api/v1/reports          — Audit reports (read-only)
/api/v1/audit-log        — Audit log entries (read-only)
/api/v1/learning/*       — Learning tracks, items, routines, activity
```

#### Auth Router (`/api/v1/auth`)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/register` | POST | No | Create user, return UserRead (201). Rejects duplicate email (409). |
| `/login` | POST | No | Validate credentials, return JWT Token (200). 401 on bad credentials. |

#### Priorities Router (`/api/v1/priorities`)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/` | POST | Yes | Create priority. 409 on cap violation. |
| `/` | GET | Yes | List priorities. Optional `?status=` filter. |
| `/{id}/cut` | POST | Yes | Cut a priority (first-class success action). |
| `/{id}/complete` | POST | Yes | Mark priority completed. |

> **Business Rule**: No PATCH endpoint for deadlines — deadlines are never extended.

#### Time Blocks Router (`/api/v1/time-blocks`)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/` | POST | Yes | Create block. Block Guard runs after insert. |
| `/` | GET | Yes | List blocks. Optional `?from=` and `?to=` filters. |
| `/{id}` | DELETE | Yes | Delete a block. |

#### Cadence Router (`/api/v1/cadence`)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/current` | GET | Yes | Get current active quarter. |
| `/quarters` | POST | Yes | Create new quarter (starts in REST phase). |
| `/tick` | POST | Yes | Advance phase state machine based on today's date. |

#### Domains Router (`/api/v1/domains`)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/` | GET | Yes | List domains, ordered by score descending. |
| `/` | POST | Yes | Create a domain. |
| `/rescore` | POST | Yes | Recompute scores for all user domains. |

#### Audits Router (`/api/v1/`)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/reports` | GET | Yes | List audit reports. Optional `?type=`, `?from=`, `?to=` filters. |
| `/audit-log` | GET | Yes | List audit log entries. Optional `?from=`, `?to=` filters. |

> **Note**: No prefix — routes are at `/api/v1/reports` and `/api/v1/audit-log` directly.

#### Learning Router (`/api/v1/learning`)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/seed-defaults` | POST | Yes | Create default Python + French tracks (idempotent). |
| `/tracks` | GET | Yes | List tracks with progress counts. |
| `/tracks/{id}` | GET | Yes | Get track detail with items, routines, streak data. |
| `/items/{id}/toggle` | POST | Yes | Toggle curriculum item PENDING ↔ DONE. |
| `/routines/{id}/log` | POST | Yes | Log practice minutes (upsert on same date). |
| `/routines/{id}/log` | DELETE | Yes | Unlog practice for a date. |
| `/activity` | GET | Yes | Heatmap data (date → count). `?days=` (7-365, default 140). |

### 4.5 Service Layer (Business Rules)

| Service | File | Rule | Trigger |
|---------|------|------|---------|
| Priority Gate | `priority_gate.py` | 1 active TECHNICAL + 1 active LANGUAGE cap | `POST /priorities` |
| Block Guard | `block_guard.py` | Flag protected window + cutoff violations (never reject) | `POST /time-blocks` |
| Cadence | `cadence.py` | Quarterly phase state machine: REST → REVIEW → SPRINT → CLOSED | `POST /cadence/tick` |
| Deadline | `deadline.py` | Force-ship at due_date (never extend) | Not triggered (no scheduler) |
| Niche Filter | `niche_filter.py` | Score domains against core assets | `POST /domains/rescore` |
| Time Audit | `time_audit.py` | Weekly proactive/reactive ratio | Not triggered (no scheduler) |
| Identity Audit | `identity_audit.py` | Weekly goal alignment check | Not triggered (no scheduler) |
| Learning | `learning.py` | Track seeding + streak computation | `POST /learning/seed-defaults` |
| Curricula | `learning_curricula.py` | Static curriculum data | Referenced by learning service |

#### Priority Gate Detail

```
get_active_count(db, user_id, track) → int
    SELECT COUNT(*) WHERE user_id=? AND track=? AND status='ACTIVE'

add_priority(db, user_id, payload) → Priority | raises PriorityCapError
    If count >= 1: find blocking priority, raise PriorityCapError
    Else: create, commit, return

cut_priority(db, priority_id) → Priority
    Set status=CUT, commit

complete_priority(db, priority_id) → Priority
    Set status=COMPLETED, commit
```

#### Block Guard Detail

```
apply_block_guard(db, block):
    1. check_protected_window(db, block) → (bool, window_id)
       - Fetch all active ProtectedWindows for user
       - Check weekday filter, category allowlist
       - Check time overlap
    2. check_cutoff(db, block) → bool
       - Fetch user.work_cutoff_time
       - Check if block.end_at > cutoff
    3. Set block.violates_protected_window and block.violates_cutoff
    4. Commit
```

#### Cadence State Machine

```
Phases: REST → REVIEW → SPRINT → CLOSED

create_quarter():
    - Calculates phase dates: REST (7 days), REVIEW (7 days), SPRINT (8 weeks)
    - Creates quarter in REST phase

tick(today):
    - REST: if today >= rest_start and < review_start → stay REST
    - REVIEW: if today >= review_start and < sprint_start → transition to REVIEW
    - SPRINT: if today >= sprint_start and < sprint_end → transition to SPRINT
    - CLOSED: if today >= sprint_end → transition to CLOSED
    - Idempotent: only transitions if current phase differs from target
```

#### Learning Streak Computation

```python
def compute_streak(logged: set[date], rest_weekdays: set[int], today: date) -> int:
    """
    Pure function. Counts consecutive logged days backwards from today.
    - Rest days neither extend nor break the streak
    - Today being unlogged does not break the streak (counts from yesterday)
    """
```

### 4.6 Pydantic Schemas

**UUID Serialization**: The `UUIDStrMixin` (in `schemas/_converters.py`) is applied to every Read schema. It uses a `@model_validator(mode="before")` to coerce UUID values to strings, handling both dict (JSON response) and ORM object input paths.

| Schema | Create Fields | Read Fields | Notes |
|--------|--------------|-------------|-------|
| `UserRegister` | email, password, stated_goal | — | `EmailStr` validation |
| `UserLogin` | email, password | — | — |
| `UserRead` | — | id, email, stated_goal, created_at | |
| `Token` | — | access_token | |
| `PriorityCreate` | title (1-255 chars), track, definition_of_done | — | |
| `PriorityRead` | — | id, title, track, status, definition_of_done | |
| `PriorityCapError` | — | blocking_priority_id, track | Custom error schema |
| `TimeBlockCreate` | category_id, start_at, end_at, notes | — | |
| `TimeBlockRead` | — | id, category_id, start_at, end_at, notes, violation flags | |
| `QuarterCreate` | year, quarter_num, theme | — | No range validation on quarter_num |
| `QuarterRead` | — | id, year, quarter_num, theme, phase, dates | |
| `DeadlineRead` | — | id, priority_id, due_date, status, scope_cuts | |
| `DomainCreate` | name, required_assets | — | |
| `DomainRead` | — | id, name, score, status, required_assets | |
| `PracticeLogCreate` | log_date, minutes (0-1440) | — | |
| `TrackRead` | — | id, slug, name, description, items_total, items_done | |
| `TrackDetailRead` | — | extends TrackRead + items + routines | |

---

## 5. Frontend Architecture

### 5.1 Application Shell

**Entry**: `index.html` → `main.tsx` → `App.tsx`

**Provider nesting order**:
```
ThemeProvider > AuthProvider > BrowserRouter > Routes
```

**Route structure**:
```
/login                          → Login (unprotected)
/                               → Layout (ProtectedRoute)
  /                             → Dashboard
  /time-blocks                  → TimeBlocks
  /priorities                   → Priorities
  /cadence                      → Cadence
  /reports                      → Reports
  /domains                      → Domains
  /audit-log                    → AuditLog
  /learning                     → Learning
```

### 5.2 Layout System

```
┌──────────────────────────────────────────────┐
│ Header (fixed top, backdrop blur)           │
├──────┬───────────────────────────────────────┤
│      │                                       │
│ Side │  <main> content area                  │
│ bar  │  (scrollable, max-w-6xl)             │
│      │                                       │
│ 256  │                                       │
│  px  │                                       │
│      │                                       │
├──────┴───────────────────────────────────────┤
```

- **Sidebar**: Collapsible (256px → 64px), 8 nav items with Lucide icons, `NavLink` active state
- **Header**: Fixed top bar with user email, theme toggle (Sun/Moon), logout, avatar
- **Main**: Scrollable content with `<Outlet />` for nested routes

### 5.3 State Management

No external state library (Redux, Zustand, etc.). State management is:

- **React Context**: `AuthContext` (user, loading, login, register, logout), `ThemeContext` (theme, toggleTheme)
- **Local state**: `useState`/`useEffect` in each page component
- **Persistence**: JWT in `localStorage('pos-token')`, user data in `localStorage('pos-user')`, theme in `localStorage('pos-theme')`

### 5.4 API Client

**File**: `src/services/api.ts`

The `ApiClient` class provides typed HTTP methods:
- `get<T>(path, params?)` — GET with query params
- `post<T>(path, body?)` — POST with JSON body
- `put<T>(path, body?)` — PUT with JSON body
- `delete<T>(path)` — DELETE

All requests include `Authorization: Bearer <token>` header. 401 responses auto-redirect to `/login` and clear the token.

API modules: `authApi`, `timeBlocksApi`, `prioritiesApi`, `cadenceApi`, `domainsApi`, `reportsApi`, `learningApi`, `auditLogApi`.

### 5.5 Charts (Pure SVG)

All charts are custom SVG implementations with no external chart library:

| Chart | Size | Technique | Used By |
|-------|------|-----------|---------|
| `ActivityHeatmap` | 20 weeks × 7 days | Grid of rectangles with teal intensity | Dashboard |
| `WeeklyHoursChart` | 7 columns | Stacked bars (indigo proactive, amber reactive) | Dashboard |
| `CategoryDonut` | 140px | `strokeDasharray`/`strokeDashoffset` arcs | Dashboard |
| `SprintRing` | Dynamic | Circular progress with phase-colored ring | Dashboard |
| `QuarterTimeline` | 4 steps | Horizontal step indicator with icons | Dashboard |
| `BarChart` | Dynamic | Generic vertical bars | Unused |
| `DonutChart` | Dynamic | Simple donut | Unused |

### 5.6 Dark Mode Implementation

Three-part system:
1. **Flash prevention** (`index.html`): Inline script reads `localStorage('pos-theme')` before paint, adds `.dark` to `<html>`
2. **Context** (`ThemeContext.tsx`): Manages state, syncs to `document.documentElement.classList`
3. **Tailwind** (`tailwind.config.js`): `darkMode: 'class'` — all components use `dark:` prefix

---

## 6. Data Model

### Entity Relationship Diagram

```mermaid
erDiagram
    USER ||--o{ TIME_BLOCK : logs
    USER ||--o{ PRIORITY : owns
    USER ||--o{ QUARTER : plans
    USER ||--o{ PROTECTED_WINDOW : configures
    USER ||--o{ TARGET_DOMAIN : evaluates
    USER ||--o{ AUDIT_REPORT : receives
    USER ||--o{ AUDIT_LOG_ENTRY : generates
    USER ||--o{ LEARNING_TRACK : learns
    USER ||--o{ PRACTICE_LOG : records

    PRIORITY ||--o| DEADLINE : has
    PRIORITY }o--|| QUARTER : belongs_to
    TIME_BLOCK }o--|| CATEGORY : classified_by
    LEARNING_TRACK ||--o{ CURRICULUM_ITEM : contains
    LEARNING_TRACK ||--o{ PRACTICE_ROUTINE : schedules
    PRACTICE_ROUTINE ||--o{ PRACTICE_LOG : tracked_by

    USER {
        UUID id PK
        String email UK
        Text password_hash
        Text stated_goal
        Time work_cutoff_time
        Int weekly_goal_hours_threshold
        DateTime created_at
        DateTime updated_at
    }

    CATEGORY {
        UUID id PK
        String name UK
        Enum classification
        Boolean goal_aligned
    }

    TIME_BLOCK {
        UUID id PK
        UUID user_id FK
        UUID category_id FK
        DateTime start_at
        DateTime end_at
        Text notes
        Boolean violates_protected_window
        Boolean violates_cutoff
    }

    PRIORITY {
        UUID id PK
        UUID user_id FK
        String title
        Enum track
        Enum status
        Text definition_of_done
        UUID quarter_id FK
    }

    QUARTER {
        UUID id PK
        UUID user_id FK
        Int year
        Int quarter_num
        Text theme
        Enum phase
        Date rest_start
        Date review_start
        Date sprint_start
        Date sprint_end
    }

    DEADLINE {
        UUID id PK
        UUID priority_id FK
        Date due_date
        Enum status
        JSON scope_cuts
    }

    PROTECTED_WINDOW {
        UUID id PK
        UUID user_id FK
        Time start_time
        Time end_time
        JSON days_of_week
        JSON allowed_category_ids
        Boolean active
    }

    TARGET_DOMAIN {
        UUID id PK
        UUID user_id FK
        String name
        JSON required_assets
        Numeric score
        Enum status
    }

    AUDIT_REPORT {
        UUID id PK
        UUID user_id FK
        Enum type
        Date period_start
        Date period_end
        JSON payload
        Enum verdict
    }

    AUDIT_LOG_ENTRY {
        UUID id PK
        UUID user_id FK
        String event_type
        String entity_type
        UUID entity_id
        JSON detail
        DateTime occurred_at
    }

    LEARNING_TRACK {
        UUID id PK
        UUID user_id FK
        String slug
        String name
        Text description
    }

    CURRICULUM_ITEM {
        UUID id PK
        UUID track_id FK
        String section
        String title
        Text details
        Int sort_order
        Enum status
        DateTime completed_at
    }

    PRACTICE_ROUTINE {
        UUID id PK
        UUID track_id FK
        String name
        Int minutes
        JSON rest_weekdays
        Int sort_order
    }

    PRACTICE_LOG {
        UUID id PK
        UUID routine_id FK
        UUID user_id FK
        Date log_date
        Int minutes
    }
```

### Table Constraints

| Table | Constraint | Type |
|-------|-----------|------|
| `users.email` | UNIQUE | Unique index |
| `time_blocks` | `end_at > start_at` | Check constraint |
| `time_blocks` | `(user_id, start_at)` | Composite index |
| `quarters` | `(user_id, year, quarter_num)` | Unique constraint |
| `learning_tracks` | `(user_id, slug)` | Unique constraint |
| `practice_logs` | `(routine_id, log_date)` | Unique constraint |

### Enumerations

| Enum | Values | Used By |
|------|--------|---------|
| `Classification` | PROACTIVE, REACTIVE, NEUTRAL | Category |
| `PriorityTrack` | TECHNICAL, LANGUAGE | Priority |
| `PriorityStatus` | ACTIVE, COMPLETED, CUT, REJECTED | Priority |
| `Phase` | REST, REVIEW, SPRINT, CLOSED | Quarter |
| `DeadlineStatus` | OPEN, SHIPPED_COMPLETE, SHIPPED_PARTIAL | Deadline |
| `DomainStatus` | ACTIVE, CUT | TargetDomain |
| `AuditType` | TIME_AUDIT, IDENTITY_AUDIT, MONTHLY_CHECKPOINT, QUARTERLY_REVIEW | AuditReport |
| `Verdict` | ALIGNED, MISALIGNED, ON_TRACK, BEHIND | AuditReport |
| `ItemStatus` | PENDING, DONE | CurriculumItem |

### Key Design Decisions

1. **No `relationship()` declarations** — All joins are manual via explicit `select()` queries. This is deliberate for clarity but means SQLAlchemy relationship features are unused.
2. **No cascade deletes** — Deleting a user leaves orphaned records. FK constraints prevent deletion if the DB enforces them.
3. **Python-side UUID generation** — `uuid.uuid4()` defaults (not `gen_random_uuid()`) for cross-DB compatibility (SQLite lacks `gen_random_uuid()`).
4. **JSON columns for arrays** — `days_of_week`, `allowed_category_ids`, `required_assets`, `scope_cuts` use `JSON` type for SQLite compatibility (Postgres would use native `ARRAY` types via Alembic).
5. **Partial unique index (not yet created)** — The priority cap's `(user_id, track) WHERE status = 'ACTIVE'` is Postgres-only and should be added via Alembic. Currently enforced at the service layer only.

---

## 7. Data Flow

### 7.1 Creating a Priority (Full Round-Trip)

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Priorities.tsx
    participant API as api.ts
    participant V as Vite Proxy
    participant R as priorities.py
    participant S as priority_gate.py
    participant DB as PostgreSQL

    U->>FE: Fill form (title, track, done criteria)
    FE->>FE: handleSubmit()
    FE->>API: prioritiesApi.create({title, track, definition_of_done})
    API->>V: POST /api/v1/priorities (Bearer token)
    V->>R: Proxy to FastAPI :8001
    R->>R: Validate PriorityCreate (Pydantic)
    R->>R: Depends(get_current_user) — decode JWT
    R->>S: add_priority(db, user.id, payload)
    S->>DB: SELECT COUNT(*) WHERE user_id=? AND track=? AND status='ACTIVE'
    alt Count >= 1
        S-->>R: Raise PriorityCapError
        R-->>V: 409 { detail: "priority_cap", blocking_priority_id, track }
        V-->>API: Error
        API-->>FE: throw {status: 409, ...}
        FE->>FE: Display "Cannot add: already have active {track} priority"
    else Count < 1
        S->>DB: INSERT INTO priorities (...)
        S->>DB: COMMIT
        S-->>R: Priority ORM instance
        R-->>V: 201 PriorityRead JSON
        V-->>API: Response
        API-->>FE: Priority object
        FE->>FE: load() — refresh priority list
    end
```

### 7.2 Time Block Creation with Block Guard

```mermaid
sequenceDiagram
    participant FE as API Client
    participant R as time_blocks.py
    participant BG as block_guard.py
    participant DB as Database

    FE->>R: POST /api/v1/time-blocks
    R->>DB: INSERT time_block (flush, no commit)
    R->>BG: apply_block_guard(db, block)
    BG->>DB: SELECT * FROM protected_windows WHERE user_id=? AND active=true
    BG->>BG: Check overlap (weekday, category, time range)
    BG->>DB: SELECT work_cutoff_time FROM users WHERE id=?
    BG->>BG: Check if block.end_at > cutoff
    BG->>DB: UPDATE block.violates_protected_window, violates_cutoff
    BG->>DB: COMMIT
    BG-->>R: Block with flags set
    R-->>FE: 201 TimeBlockRead (with violation flags)
```

### 7.3 Learning Track Streak

```mermaid
sequenceDiagram
    participant FE as Learning.tsx
    participant R as learning.py router
    participant S as learning.py service
    participant DB as Database

    FE->>R: GET /api/v1/learning/tracks/{id}
    R->>DB: SELECT track WHERE id=? AND user_id=?
    R->>DB: SELECT items WHERE track_id=?
    R->>DB: SELECT routines WHERE track_id=?
    R->>DB: SELECT logs WHERE routine_id IN (...) AND user_id=?

    loop For each routine
        R->>S: compute_streak(logged_dates, rest_weekdays, today)
        S-->>R: streak_count (int)
    end

    R->>R: Build response with streak per routine
    R-->>FE: 200 TrackDetailRead
```

---

## 8. Business Rules Engine

### 8.1 Priority Gate

**Rule**: Hard cap of 1 active priority per track (TECHNICAL or LANGUAGE).

```
State transitions:
  ACTIVE → COMPLETED  (via /complete)
  ACTIVE → CUT        (via /cut)

Cap enforcement:
  Before INSERT: COUNT(*) WHERE status='ACTIVE' AND track=X
  If count >= 1: HTTP 409 with blocking priority details
```

**Enforcement point**: Service layer (`priority_gate.py:add_priority`). Also has a comment about a Postgres partial unique index `(user_id, track) WHERE status = 'ACTIVE'` but this has not been created via Alembic.

### 8.2 Deadline Enforcer

**Rule**: At `due_date`, if priority is not COMPLETED → forced ship (`SHIPPED_PARTIAL`). Never extend deadlines.

```
enforce(deadline_id):
  Fetch deadline + priority
  If priority.status != COMPLETED:
    deadline.status = SHIPPED_PARTIAL
    priority.status = COMPLETED
  COMMIT
```

**Status**: Implemented but **never triggered** — no background job or scheduler invokes this.

### 8.3 Block Guard

**Rule**: Every hour accounted for as a row. Block Guard flags violations but never rejects inserts.

```
Violations flagged:
  1. Protected Window overlap (time range + weekday + category filter)
  2. Cutoff violation (block.end_at > user.work_cutoff_time)

Both are stored as boolean flags on the TimeBlock record.
```

### 8.4 Cadence State Machine

```
Quarter phases: REST → REVIEW → SPRINT → CLOSED

Timeline (from create_quarter):
  Day 0-6:    REST phase
  Day 7-13:   REVIEW phase
  Day 14-69:  SPRINT phase (8 weeks)
  Day 70+:    CLOSED

tick() transitions based on today's date relative to phase boundaries.
Idempotent: only transitions if current phase differs from target.
```

### 8.5 Niche Filter

**Rule**: Score job-search domains against core assets.

```
score(domain):
  required = domain.required_assets  # list[str]
  score = len(required) / max(len(required), 1)
  # Simplifies to: 1.0 if assets exist, 0.0 if empty

  If score < threshold (0.5):
    status = CUT
```

> **Known issue**: The scoring logic is trivial — any domain with ≥1 required asset scores 1.0.

### 8.6 Learning Streaks

```
compute_streak(logged, rest_weekdays, today):
  Start from today, move backwards
  - If today is logged: count it
  - If today is a rest day: skip (don't count, don't break)
  - If today is logged: increment streak
  - If today is not logged and not rest day: streak breaks

  Return consecutive count of logged/rest days from today backwards
```

---

## 9. Authentication & Security

### 9.1 Authentication Flow

```mermaid
sequenceDiagram
    participant U as Browser
    participant FE as AuthContext
    participant API as /api/v1/auth/login
    participant SEC as security.py
    participant DB as Database

    U->>FE: Submit credentials
    FE->>API: POST /auth/login {email, password}
    API->>DB: SELECT user WHERE email=?
    API->>SEC: verify_password(plain, hash)
    SEC-->>API: True
    API->>SEC: create_access_token(user.id)
    SEC-->>API: JWT token (HS256, 24h expiry)
    API-->>FE: {access_token: "eyJ..."}
    FE->>FE: Decode JWT (atob) to extract user ID
    FE->>FE: Store token + user in localStorage
    FE->>FE: Set user state (triggers re-render)
```

### 9.2 JWT Configuration

| Property | Value |
|----------|-------|
| Algorithm | HS256 (symmetric) |
| Secret | `JWT_SECRET` env var (default: `change-me-in-production`) |
| Expiry | 24 hours (configurable via `JWT_EXPIRE_MINUTES`) |
| Payload | `{"sub": user_id, "exp": expire_datetime}` |
| Extraction | `OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")` |

### 9.3 Password Hashing

| Property | Value |
|----------|-------|
| Library | passlib CryptContext |
| Algorithm | bcrypt |
| Pinned version | bcrypt==4.1.x (passlib incompatible with 5.x) |
| Hash format | `$2b$...` (auto-upgraded by passlib) |

### 9.4 Security Patterns

**SQL Injection Protection**: All queries use SQLAlchemy's parameterized query builder or `text()` with named parameters. No raw string interpolation of user input into SQL.

**Input Validation**: Pydantic schemas enforce field constraints at the API boundary.

**Auth Enforcement**: Every protected route uses `Depends(get_current_user)`. The dependency:
1. Extracts JWT from `Authorization: Bearer` header
2. Decodes and validates the token (checks expiry, signature)
3. Looks up user by ID
4. Raises 401 if invalid or missing

**Ownership Checks**: Most endpoints verify `user_id` matches the authenticated user before returning data.

### 9.5 Security Considerations

| Concern | Status | Notes |
|---------|--------|-------|
| Rate limiting on login | Not implemented | No protection against brute-force |
| Password complexity | Not enforced | Any string accepted |
| Token refresh | Not implemented | Users must re-login after 24h |
| Token revocation | Not implemented | Stolen tokens valid until expiry |
| CORS production | Hardcoded localhost | Would break behind different origin |
| JWT secret | Default in config | Must be overridden in production |

---

## 10. External Dependencies

### Backend Python Packages

| Package | Purpose | Notes |
|---------|---------|-------|
| fastapi | Web framework | Async, automatic OpenAPI docs |
| uvicorn | ASGI server | Development server |
| sqlalchemy[asyncio] | ORM + async DB | SQLAlchemy 2.0 style |
| asyncpg | PostgreSQL driver | Async PostgreSQL adapter |
| aiosqlite | SQLite driver | Async SQLite adapter (dev/tests) |
| alembic | Database migrations | Configured but no versions |
| pydantic | Data validation | v2 with PydanticSettings |
| pydantic-settings | Env config | `.env` file loading |
| python-jose[cryptography] | JWT tokens | HS256 encoding/decoding |
| passlib[bcrypt] | Password hashing | bcrypt backend |
| bcrypt | Hash backend | Pinned to 4.1.x for passlib compat |
| python-multipart | Form data | OAuth2 token extraction |
| httpx | HTTP client | Used in tests with ASGITransport |
| pytest | Test framework | |
| pytest-asyncio | Async tests | `asyncio_mode = "auto"` |
| freezegun | Time mocking | For testing time-dependent logic |
| ruff | Linter | line-length 100, py310 target |
| mypy | Type checker | Strict mode + pydantic plugin |

### Frontend npm Packages

| Package | Version | Purpose |
|---------|---------|---------|
| react | ^18.3.1 | UI framework |
| react-dom | ^18.3.1 | DOM rendering |
| react-router-dom | ^7.18.1 | Client-side routing |
| lucide-react | ^1.24.0 | Icon library |
| vite | ^5.4.10 | Build tool + dev server |
| typescript | ^5.6.2 | Type checking |
| tailwindcss | ^3.4.19 | Utility CSS |
| @vitejs/plugin-react | — | React support for Vite |
| eslint | ^9.0.0 | Linting |
| eslint-plugin-react-hooks | — | Hooks rules |
| eslint-plugin-react-refresh | — | Fast refresh rules |
| autoprefixer | — | CSS vendor prefixes |
| @types/react | — | React type definitions |
| @types/react-dom | — | React DOM type definitions |

### External Services (CDN)

| Service | URL | Purpose |
|---------|-----|---------|
| Google Fonts | fonts.googleapis.com | Inter font (weights 400-700) |

---

## 11. Environment Configuration

### Backend `.env` Variables

| Variable | Required | Default | Example |
|----------|----------|---------|---------|
| `DATABASE_URL` | Yes | `postgresql+asyncpg://pos:pos@localhost:5432/pos` | `postgresql+asyncpg://user:pass@host:5432/db` |
| `JWT_SECRET` | Yes | `change-me-in-production` | `your-256-bit-secret-key` |
| `JWT_EXPIRE_MINUTES` | No | 1440 (24h) | `60` |

### Docker Compose Environment

| Service | Variable | Value |
|---------|----------|-------|
| api | `DATABASE_URL` | `postgresql+asyncpg://pos:pos@db:5432/pos` |
| api | `JWT_SECRET` | `dev-secret-change-in-prod` |
| db | `POSTGRES_USER` | `pos` |
| db | `POSTGRES_PASSWORD` | `pos` |
| db | `POSTGRES_DB` | `pos` |

### Frontend Configuration

| Setting | Value | Source |
|---------|-------|--------|
| Dev server port | 5174 | `vite.config.ts` |
| API proxy target | `http://127.0.0.1:8001` | `vite.config.ts` |
| Dark mode | `localStorage('pos-theme')` | `ThemeContext.tsx` |
| Auth token | `localStorage('pos-token')` | `AuthContext.tsx` |

### CORS Configuration

| Setting | Value |
|---------|-------|
| `allow_origins` | `["http://localhost:5173"]` |
| `allow_credentials` | `True` |
| `allow_methods` | `["*"]` |
| `allow_headers` | `["*"]` |

> **Note**: CORS origin doesn't match actual dev port (5174). Production would need updating.

---

## 12. Docker & Deployment

### docker-compose.yml (3 Services)

```yaml
services:
  db:
    image: postgres:16
    ports: 5432:5432
    healthcheck: pg_isready
    volume: pgdata

  api:
    build: ./backend
    ports: 8000:8000
    depends_on: db (healthy)
    env: DATABASE_URL, JWT_SECRET

  frontend:
    build: ./frontend
    ports: 3000:80
    depends_on: api
```

### Backend Dockerfile

```
python:3.11-slim → install requirements.txt → create non-root user → uvicorn
```

- No Alembic migration step (relies on `create_all()`)
- No health check defined
- Non-root user (appuser, uid 1000)

### Frontend Dockerfile

```
Build stage: node:20-alpine → npm ci → npm run build
Serve stage: nginx:alpine → copy dist + nginx.conf
```

- Multi-stage build for small production image
- nginx serves static files with SPA fallback
- `/api` requests proxied to `http://api:8000`

### nginx.conf Highlights

- SPA fallback: `try_files $uri $uri/ /index.html`
- API proxy: `/api/` → `http://api:8000`
- Static caching: 1 year, immutable headers for js/css/images/fonts

---

## 13. Testing

### Test Infrastructure

| Component | Configuration |
|-----------|--------------|
| Framework | pytest + pytest-asyncio |
| Mode | `asyncio_mode = "auto"` |
| DB | SQLite in-memory (`sqlite+aiosqlite:///./test.db`) |
| Client | httpx `AsyncClient` with `ASGITransport` |
| Fixtures | `db_engine`, `db_session`, `client`, `test_user`, `auth_token`, `auth_headers` |

### Test Coverage

| File | Tests | What's Tested |
|------|-------|---------------|
| `test_auth.py` | 5 | Register, login, duplicate email, wrong password, 401 |
| `test_priorities.py` | 4 | Create, 409 cap, cut, list |
| `test_time_blocks.py` | 3 | Create, list, auth required |
| `test_cadence.py` | 3 | Create quarter, get current, tick |
| `test_learning.py` | 6 | Seed, idempotent, detail, toggle, log, ownership |
| `test_priority_gate.py` | 4 | Service-level cap enforcement |
| `test_learning_streak.py` | 7 | Streak computation (pure function) |
| **Total** | **32** | |

### Test Execution

```bash
cd backend
rm -f test.db
PYTHONPATH=. python3 -m pytest tests/ -v
```

### Known Test Issues

- `test_time_blocks.py` accepts status codes `(201, 422, 500)` — a 500 would pass
- No tests for `time_audit.py` or `identity_audit.py` (Postgres-only `func.extract`)
- No tests for deadline enforcement (service exists but is never called)
- SQLite tests may pass but Postgres would fail for `func.extract("epoch")` queries

---

## 14. Known Limitations

### Critical

1. **No Alembic migrations** — Schema management relies entirely on `create_all()`. No ability to upgrade/downgrade schemas in production.
2. **`datetime.utcnow()` deprecated** — Used in 34 places. Will be removed in future Python versions.
3. **Dev port mismatch** — Vite runs on :5174 proxying to :8001, but CORS allows :5173 and docs say :5173/:8000.

### High

4. **No pagination** — All list endpoints return every row. Performance degrades as data grows.
5. **Zero application logging** — No `import logging` anywhere. Production debugging is impossible.
6. **No root `.gitignore`** — `test.db`, `__pycache__`, `.env` files unprotected.
7. **Broken niche filter scoring** — Any domain with ≥1 required asset scores 1.0.
8. **Config drift** — `pyproject.toml` and `requirements.txt` diverge (bcrypt pin, pydantic[email]).

### Medium

9. **Dead code** — `events/` module empty, `deadline.py` service never triggered.
10. **Missing DB indexes** — Most FK columns lack indexes (fine for single-user, problematic at scale).
11. **No password policy** — Any string accepted as password.
12. **Postgres-only SQL** — `func.extract("epoch")` in audit services fails on SQLite.
13. **Unused config values** — `sprint_length_weeks`, `rest_phase_days`, etc. defined but never referenced.
14. **No cascade deletes** — Deleting a user leaves orphaned records.

### Low

15. **No 404 route** — Undefined paths render blank.
16. **Full page reloads** — Dashboard uses `<a href>` instead of React Router `<Link>`.
17. **No token refresh** — Expired tokens require re-login.
18. **Dead chart components** — `BarChart` and `DonutChart` unused.
19. **Stale documentation** — `AGENTS.md` claims 19 tests (actual: 32), references nonexistent E2E test.

---

*Generated from full codebase audit — all source files, configs, tests, and infrastructure reviewed.*

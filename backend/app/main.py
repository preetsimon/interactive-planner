import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.api.v1.router import api_router
from app.db.base import engine, async_session_factory
from app.db.base import Base
from app.db.seed import seed_categories
from app.db.migrate import run_migrations
# Ensure all models are registered with Base.metadata before create_all
from app.models import user, category, time_block, priority, quarter, deadline, protected_window, domain, audit, learning  # noqa: F401

STATIC_DIR = Path(os.environ.get("POS_STATIC_DIR", "/opt/pos/static"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables (dev only — use Alembic in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await run_migrations(conn)

    # Seed categories
    async with async_session_factory() as session:
        await seed_categories(session)

    yield

    await engine.dispose()


app = FastAPI(
    title="POS — Personal Operating System",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
async def health():
    return {"status": "ok"}


if STATIC_DIR.is_dir():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="static")

    @app.get("/{path:path}")
    async def spa_fallback(path: str):
        file = STATIC_DIR / path
        if file.is_file() and ".." not in path:
            return FileResponse(file)
        return FileResponse(STATIC_DIR / "index.html")

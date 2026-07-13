from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.db.base import engine, async_session_factory
from app.db.base import Base
from app.db.seed import seed_categories
# Ensure all models are registered with Base.metadata before create_all
from app.models import user, category, time_block, priority, quarter, deadline, protected_window, domain, audit, learning  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables (dev only — use Alembic in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

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
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
async def health():
    return {"status": "ok"}

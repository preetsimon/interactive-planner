import uuid
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base, get_db
from app.main import app
from app.core.security import hash_password, create_access_token
from app.models.user import User

# Import all models so Base.metadata knows every table
from app.models import user, category, time_block, priority, quarter, deadline, protected_window, domain, audit, learning  # noqa: F401

TEST_DB_URL = "sqlite+aiosqlite:///./test.db"


@pytest_asyncio.fixture
async def db_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    session_factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_engine):
    session_factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        password_hash=hash_password("secret123"),
        stated_goal="Backend engineer + professional French",
        weekly_goal_hours_threshold=10,
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest_asyncio.fixture
async def auth_token(test_user: User):
    return create_access_token(str(test_user.id))


@pytest_asyncio.fixture
async def auth_headers(auth_token: str):
    return {"Authorization": f"Bearer {auth_token}"}

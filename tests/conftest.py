import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.database import get_session
from src.main import app
from src.models import Base


@pytest.fixture
async def client(tmp_path):
    database_path = tmp_path / "test_movies.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    test_session = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async def override_get_session():
        async with test_session() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        await engine.dispose()

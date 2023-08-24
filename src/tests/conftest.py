import asyncio

import pytest
import pytest_asyncio
from accentdatabase.testing import recreate_postgres_database
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.testclient import TestClient

from app.auth.dependencies import current_user
from app.auth.exceptions import Unauthorized
from app.auth.schemas import UserRead, UserType
from app.config import settings
from app.database import tables  # noqa: F401
from app.database.engine import engine
from app.database.session import async_session, get_session
from app.main import app
from tests import fixtures


def run_alembic_upgrade(connection, cfg):
    cfg.attributes["connection"] = connection
    command.upgrade(cfg, "head")


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(name="db_setup", scope="session", autouse=True)
async def db_setup_fixture():
    await recreate_postgres_database(settings.database_url)


@pytest_asyncio.fixture(name="db_migrations", scope="session", autouse=True)
async def db_migrations_fixture(db_setup):
    async with engine.begin() as conn:
        await conn.run_sync(run_alembic_upgrade, Config("alembic.ini"))
        # load fixtures
        await conn.execute(fixtures.user_type_sql, fixtures.user_type)
        await conn.execute(fixtures.user_sql, fixtures.user)
    await engine.dispose()


@pytest_asyncio.fixture(name="db_session")
async def db_session_fixture():
    connection = await engine.connect()
    trans = await connection.begin()
    async with async_session(bind=connection) as session:
        yield session

    await trans.rollback()
    await connection.close()


@pytest.fixture
def client_authenticated(db_session: AsyncSession) -> TestClient:
    def mock_user():
        user_type = UserType(**fixtures.user_type, scopes=["admin"])
        return UserRead(**fixtures.user, user_type=user_type)

    app.dependency_overrides[get_session] = lambda: db_session
    app.dependency_overrides[current_user] = mock_user
    yield TestClient(app)
    app.dependency_overrides = {}


@pytest.fixture
def client_unauthenticated() -> TestClient:
    def no_auth():
        raise Unauthorized()

    app.dependency_overrides[current_user] = no_auth
    yield TestClient(app)
    app.dependency_overrides = {}

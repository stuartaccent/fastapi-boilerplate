# isort: off
import asyncio
import contextlib
from os import environ

if environ.get("TEST_DATABASE_URL"):
    environ["DATABASE_URL"] = environ["TEST_DATABASE_URL"]

import pytest
import pytest_asyncio
from accentdatabase.config import config
from accentdatabase.engine import engine
from accentdatabase.session import get_session
from accentdatabase.testing import recreate_postgres_database
from alembic import command
from alembic.config import Config
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.authentication.dependencies import get_user_service
from app.authentication.password import hash_password
from app.database import tables
from app.database.tables import User
from app.main import app


def run_alembic_upgrade(connection, cfg):
    cfg.attributes["connection"] = connection
    command.upgrade(cfg, "head")


@pytest.fixture(scope="session")
def event_loop(request):
    """pytest fixture to create an event loop"""

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(name="db_setup", scope="session", autouse=True)
async def db_setup_fixture():
    await recreate_postgres_database(config.url)


@pytest_asyncio.fixture(name="db_migrations", scope="session", autouse=True)
async def db_migrations_fixture(db_setup):
    async with engine.begin() as conn:
        await conn.run_sync(run_alembic_upgrade, Config("alembic.ini"))

    # dispose the engine
    await engine.dispose()


@pytest_asyncio.fixture(name="db_session")
async def db_session_fixture():
    """create a sqlalchemy session"""

    # create a sqlalchemy connection
    connection = await engine.connect()
    # begin a new database transaction
    trans = await connection.begin()
    # create a sessionmaker
    async_session = sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    # create a new session and bind it to the connection
    # this will ensure that when the transaction is rolled back
    # all calls to the session's commit will be rolled back as well
    async with async_session(bind=connection) as session:
        yield session

    # rollback the transaction
    await trans.rollback()
    # close the connection
    await connection.close()


@pytest_asyncio.fixture(name="client")
async def client_fixture(db_session: AsyncSession):
    """the client to use in the tests"""

    # override the database session for the app
    # this is to ensure that the database session is always the same
    # as the one used in the tests so that the session commits are
    # always rolled back in the session fixture above
    app.dependency_overrides[get_session] = lambda: db_session
    # create a client
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    # restore the original database session
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(name="user")
async def create_user(db_session: AsyncSession):
    user = User(
        first_name="Some",
        last_name="One",
        email="someone@example.com",
        hashed_password=hash_password("password"),
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest_asyncio.fixture(name="login_token")
async def get_login_token(user: User, db_session: AsyncSession):
    get_user_service_ctx = contextlib.asynccontextmanager(get_user_service)
    async with get_user_service_ctx(db_session) as user_service:
        return await user_service.create_token(user, 10)

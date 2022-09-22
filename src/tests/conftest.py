# isort: off

import asyncio
import contextlib
from copy import deepcopy

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from starlette import status

from app.database import tables

from app.api.schemas import UserCreate
from app.config import settings
from app.database.session import get_session
from app.encoders import json_serializer
from app.main import app
from app.users import get_user_manager, get_user_db

db_url = deepcopy(settings.database_url)
db_url_test = db_url.replace(db_url.path, f"{db_url.path}_test")
db_url_maintenance = db_url.replace(db_url.path, "/postgres")
db_test = db_url_test.split("/")[-1]


def run_alembic_upgrade(connection, cfg):
    cfg.attributes["connection"] = connection
    command.upgrade(cfg, "head")


@pytest.fixture(scope="session")
def event_loop(request):
    """pytest fixture to create an event loop"""

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def db_fixture():
    """
    Drop and recreate our test database
    This happens only once per test session.
    """

    engine = create_async_engine(db_url_maintenance, isolation_level="AUTOCOMMIT")
    async with engine.begin() as conn:
        # drop all active database sessions
        await conn.execute(
            text(
                f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{db_test}'
            AND pid <> pg_backend_pid();"""
            )
        )
        # drop the test database
        await conn.execute(text(f"DROP DATABASE IF EXISTS {db_test};"))
        # create the test database
        await conn.execute(text(f"CREATE DATABASE {db_test};"))

    # dispose of the engine
    await engine.dispose()

    # run the migrations using alembic
    engine = create_async_engine(db_url_test, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(run_alembic_upgrade, Config("alembic.ini"))

    # dispose the engine
    await engine.dispose()


@pytest_asyncio.fixture(name="engine", scope="session")
async def engine_fixture():
    """create a sqlalchemy engine to use for the entire test session"""

    # create a sqlalchemy engine
    engine = create_async_engine(
        db_url_test,
        future=True,
        json_serializer=json_serializer,
        echo=False,
    )
    yield engine
    # dispose the engine
    await engine.dispose()


@pytest_asyncio.fixture(name="db_session")
async def session_fixture(engine):
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
    get_user_db_context = contextlib.asynccontextmanager(get_user_db)
    get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)

    async with get_user_db_context(db_session) as user_db:
        async with get_user_manager_context(user_db) as user_manager:
            user = await user_manager.create(
                UserCreate(
                    first_name="Some",
                    last_name="One",
                    email="someone@example.com",
                    password="password",
                )
            )
            user.is_verified = True
            db_session.add(user)
            await db_session.commit()
            return user


@pytest_asyncio.fixture(name="login_token")
async def get_login_token(client: AsyncClient, user: tables.User):
    response = await client.post(
        "/auth/token/login",
        data={
            "username": user.email,
            "password": "password",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    return response.json()["access_token"]

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.database.engine import engine

async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    This method is an async context manager that provides an asynchronous SQLAlchemy session.

    @return: An async generator that yields an asynchronous SQLAlchemy session object.

    Example usage:
    ```
    from app.database.session import get_session

    async with get_session() as session:
        # Use the session object for database operations
        await session.execute(...)
    ```
    """

    async with async_session() as session:
        yield session


async def get_session_dependency() -> AsyncSession:
    """
    Get a dependency for an asynchronous SQLAlchemy session.

    @return: An asynchronous SQLAlchemy session.
    @rtype: sqlalchemy.ext.asyncio.AsyncSession

    Example usage:
    ```
    from app.database.session import get_session

    @app.get("")
    async def endpoint(session: AsyncSession = Depends(get_session_dependency)):
        # Use the session object for database operations
        return await session.scalars(...)
    ```
    """

    async with get_session() as session:
        yield session

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.database.engine import engine

async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    returns an async session object.
    - example FastAPI usage::
        from app.database.session import get_session
        from fastapi import Depends, FastApi
        from sqlalchemy import select
        from sqlalchemy.ext.asyncio import AsyncSession
        app = FastAPI()
        @app.get("/items")
        async def items(session: AsyncSession = Depends(get_session)):
            qs = select(Item)
            return (await session.execute(qs)).scalars().all()
    """

    async with async_session() as session:
        yield session

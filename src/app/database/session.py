from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.config import settings
from app.encoders import json_serializer

engine = create_async_engine(
    settings.database_url,
    future=True,
    json_serializer=json_serializer,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

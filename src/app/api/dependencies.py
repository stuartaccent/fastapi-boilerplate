from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.database.tables import Message


async def get_message(
    id: UUID,
    session: AsyncSession = Depends(get_session)
) -> Message:
    # statement = select(Message).where(Message.id == id)
    # message = (await session.execute(statement)).scalar_one_or_none()
    # if not message:
    #     raise HTTPException(404)
    # return message
    if message := await session.get(Message, id):
        return message
    raise HTTPException(404)

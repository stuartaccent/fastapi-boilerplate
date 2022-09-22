from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import MessageRead
from app.database.session import get_session
from app.database.tables import Message

router = APIRouter()


@router.get("/", response_model=List[MessageRead])
async def list_messages(session: AsyncSession = Depends(get_session)):
    statement = select(Message)
    return list((await session.execute(statement)).scalars())

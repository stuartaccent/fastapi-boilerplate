from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response

from app.api.schemas import MessageRead
from app.database.session import get_session
from app.database.tables import Message

router = APIRouter()


@router.get("/", response_model=List[MessageRead])
async def list_messages(session: AsyncSession = Depends(get_session)):
    statement = select(Message)
    return list((await session.execute(statement)).scalars())


@router.get("/{id}", response_model=MessageRead)
async def get_messages(
    id: UUID,
    session: AsyncSession = Depends(get_session)
):
    statement = select(Message).where(Message.id == id)
    message = (await session.execute(statement)).scalar()
    if not message:
        raise HTTPException(404)
    return message


@router.delete("/{id}", response_class=Response, status_code=204)
async def delete_messages(
    id: UUID,
    session: AsyncSession = Depends(get_session)
):
    statement = select(Message).where(Message.id == id)
    message = (await session.execute(statement)).scalar()
    if not message:
        raise HTTPException(404)
    await session.delete(message)
    await session.commit()

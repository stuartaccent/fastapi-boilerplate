from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import MessageRead
from app.database.tables import Message

pytestmark = pytest.mark.asyncio


async def test_is_valid_form_dict():
    data = {"id": uuid4(), "comment": "hello"}
    assert MessageRead.parse_obj(data).dict() == data


async def test_is_valid_from_orm(db_session: AsyncSession):
    data = {"comment": "hello"}
    message = Message(**data)
    db_session.add(message)
    await db_session.commit()
    assert MessageRead.from_orm(message).dict() == {
        "id": message.id,
        "comment": message.comment,
    }

import time
from copy import deepcopy
from typing import Any, Dict
from uuid import UUID

from app.database.tables import Collection, Field, Form
from app.database.utils import DatabaseUtils


async def create_collection(
    db: DatabaseUtils,
    owner_id: UUID,
    extra: Dict[str, Any] | None = None,
) -> Collection:
    collection_data = {
        "name": "default",
        "owner_id": owner_id,
    }
    if extra:
        collection_data |= extra
    return await db.add(Collection, collection_data)


async def create_field(
    data: Dict[str, Any],
    form_id: UUID,
    db: DatabaseUtils,
) -> Field:
    field_data = deepcopy(data)
    field_data["form_id"] = form_id
    return await db.add(Field, field_data)


async def create_form(
    db: DatabaseUtils,
    owner_id: UUID,
    extra: Dict[str, Any] | None = None,
) -> Form:
    form_data = {
        "name": "my_form",
        "description": "my form description",
        "accept_submissions_as_json": True,
        "accept_submissions_as_form_data": False,
        "submission_retention_days": 30,
        "token": str(time.time()),
    }
    if not extra or "collection_id" not in extra:
        collection = await create_collection(db, owner_id)
        form_data["collection_id"] = collection.id
    if extra:
        form_data |= extra
    return await db.add(Form, form_data)

import json

from sqlalchemy.ext.asyncio import create_async_engine

from app.config import settings

engine = create_async_engine(
    str(settings.database_url),
    json_serializer=json.dumps,
    future=True,
    echo=False,
)

from accentdatabase.encoders import json_serializer
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import settings

engine = create_async_engine(
    str(settings.database_url),
    json_serializer=json_serializer,
    future=True,
    echo=False,
)

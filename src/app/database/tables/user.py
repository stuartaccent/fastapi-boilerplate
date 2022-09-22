from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import Column, DateTime, String, text
from sqlalchemy.dialects.postgresql import UUID

from .base import Base


class User(SQLAlchemyBaseUserTable, Base):
    __tablename__ = "users"
    __mapper_args__ = {"eager_defaults": True}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        server_default=text("gen_random_uuid()"),
        nullable=False,
    )
    first_name = Column(
        String(120),
        nullable=False,
    )
    last_name = Column(
        String(120),
        nullable=False,
    )
    created_at = Column(
        DateTime,
        server_default=text("clock_timestamp()"),
        nullable=False,
    )

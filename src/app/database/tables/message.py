from sqlalchemy import Column, DateTime, Text, text
from sqlalchemy.dialects.postgresql import UUID

from .base import Base


class Message(Base):
    __tablename__ = "messages"
    __mapper_args__ = {"eager_defaults": True}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        server_default=text("gen_random_uuid()"),
        nullable=False,
    )
    comment = Column(
        Text,
        nullable=False,
    )
    created_at = Column(
        DateTime,
        server_default=text("clock_timestamp()"),
        nullable=False,
    )

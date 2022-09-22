from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyBaseAccessTokenTable
from sqlalchemy import Column, ForeignKey, Integer, text
from sqlalchemy.dialects.postgresql import UUID

from .base import Base


class AccessToken(SQLAlchemyBaseAccessTokenTable, Base):
    __tablename__ = "accesstokens"
    __mapper_args__ = {"eager_defaults": True}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        server_default=text("gen_random_uuid()"),
        nullable=False,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

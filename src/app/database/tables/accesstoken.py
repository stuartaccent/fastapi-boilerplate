from accentdatabase.base import Base
from accentdatabase.mixins import UUIDMixin
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyBaseAccessTokenTable
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


class AccessToken(SQLAlchemyBaseAccessTokenTable, UUIDMixin, Base):
    __tablename__ = "accesstokens"
    __mapper_args__ = {"eager_defaults": True}

    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
    )

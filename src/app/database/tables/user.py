from datetime import datetime

from accentdatabase.base import Base
from accentdatabase.mixins import UUIDMixin
from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import String, text
from sqlalchemy.orm import Mapped, mapped_column


class User(SQLAlchemyBaseUserTable, UUIDMixin, Base):
    __tablename__ = "users"
    __mapper_args__ = {"eager_defaults": True}

    first_name: Mapped[str] = mapped_column(
        String(120),
    )
    last_name: Mapped[str] = mapped_column(
        String(120),
    )
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("clock_timestamp()"),
    )

from datetime import datetime

from accentdatabase.base import Base
from accentdatabase.mixins import UUIDMixin
from sqlalchemy import Boolean, String, text
from sqlalchemy.orm import Mapped, mapped_column


class User(UUIDMixin, Base):
    __tablename__ = "users"
    __mapper_args__ = {"eager_defaults": True}

    email: Mapped[str] = mapped_column(
        String(length=320),
        unique=True,
        index=True,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(1024),
    )
    first_name: Mapped[str] = mapped_column(
        String(120),
    )
    last_name: Mapped[str] = mapped_column(
        String(120),
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("clock_timestamp()"),
    )

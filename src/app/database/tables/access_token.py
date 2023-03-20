import uuid
from datetime import datetime

from accentdatabase.base import Base
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class AccessToken(Base):
    __tablename__ = "access_tokens"
    __mapper_args__ = {"eager_defaults": True}

    id = None  # remove the id pk
    token: Mapped[str] = mapped_column(
        String(1024),
        primary_key=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )

    user = relationship("User")

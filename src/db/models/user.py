import datetime
from typing import List
from uuid import uuid4

from sqlalchemy import DateTime
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.db.models.base import Base


class User(Base):
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column(nullable=False)
    conversations: Mapped[List["Conversation"]] = relationship(
        "Conversation", back_populates="user", default_factory=list
    )
    id: str = mapped_column(primary_key=True, default_factory=lambda: str(uuid4()))
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
        nullable=False,
    )

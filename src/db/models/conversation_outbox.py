import datetime
from typing import Optional

from sqlalchemy import Integer, JSON, Boolean, DateTime, String, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from src.db.models.base import Base


class ConversationOutbox(Base):
    __tablename__ = "conversation_outbox"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    conversation_id: Mapped[str] = mapped_column(nullable=False)
    is_processed: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
    )
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        nullable=True, default=None
    )
    payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=None)

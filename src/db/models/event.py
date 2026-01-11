import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from sqlalchemy import JSON, DateTime, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped

from src.db.models.base import Base


class EventType(str, Enum):
    CONVERSATION_STARTED = "conversation_started"
    NEW_MESSAGE = "new_message"
    CONVERSATION_DELETED = "conversation_deleted"


class ConversationEvent(Base):
    __tablename__ = "conversations_events"
    conversation_id: Mapped[str] = mapped_column(nullable=False)
    version: Mapped[int] = mapped_column(nullable=False)
    type: Mapped[EventType] = mapped_column(nullable=False)
    payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=None)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
        nullable=False,
    )
    id: Mapped[str] = mapped_column(
        primary_key=True, default_factory=lambda: str(uuid4()), nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "conversation_id", "version", name="uq_conversation_id_version"
        ),
    )

import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy.orm import mapped_column

from src.db.models.base import Base


class EventType(str, Enum):
    CONVERSATION_STARTED = "conversation_started"
    NEW_MESSAGE = "new_message"
    CONVERSATION_DELETED = "conversation_deleted"


class ConversationEvent(Base):
    __tablename__ = "conversations_events"
    conversation_id: str = mapped_column(ForeignKey("conversations.id"))
    type: EventType = mapped_column(String, nullable=False)
    payload: Optional[dict] = mapped_column(JSON, nullable=True, default=None)
    timestamp: datetime.datetime = mapped_column(
        DateTime(timezone=True),
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
        nullable=False,
    )
    id: str = mapped_column(
        primary_key=True, default_factory=lambda: str(uuid4()), nullable=False
    )

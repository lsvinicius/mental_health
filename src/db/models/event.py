import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import JSON, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.db.models.base import Base


class EventType(str, Enum):
    CONVERSATION_STARTED = "conversation_started"
    NEW_MESSAGE = "new_message"


class ConversationEvent(Base):
    __tablename__ = "conversations_events"
    conversation_id: str = mapped_column(ForeignKey("conversations.id"))
    type: EventType
    payload: dict = mapped_column(JSON, nullable=True, default=None)
    timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now(datetime.UTC), nullable=False
    )
    id: str = mapped_column(primary_key=True, default=uuid4, nullable=False)

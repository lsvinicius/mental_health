import datetime
from typing import Optional

from sqlalchemy import Integer, JSON, Boolean, DateTime, String, ForeignKey
from sqlalchemy.orm import mapped_column

from src.db.models.base import Base


class ConversationOutbox(Base):
    __tablename__ = "conversation_outbox"
    id: int = mapped_column(Integer, primary_key=True, autoincrement=True, init=False)
    payload: dict = mapped_column(JSON)
    conversation_id: str = mapped_column(
        String, ForeignKey("conversations.id"), nullable=False
    )
    is_processed: bool = mapped_column(Boolean, default=False, nullable=False)
    created_at: datetime.datetime = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
    )
    updated_at: Optional[datetime.datetime] = mapped_column(nullable=True, default=None)

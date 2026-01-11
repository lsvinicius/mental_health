import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.db.models.base import Base
from src.db.models.event import ConversationEvent


class ConversationOutbox(Base):
    __tablename__ = "conversation_outbox"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    event_id: Mapped[str] = mapped_column(
        ForeignKey(ConversationEvent.id), nullable=False
    )
    event: Mapped[ConversationEvent] = relationship("ConversationEvent")
    is_processed: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
    )
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )

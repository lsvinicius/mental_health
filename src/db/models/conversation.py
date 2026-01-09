from typing import List
from uuid import uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, relationship

from src.db.models.base import Base
from src.db.models.event import ConversationEvent


class Conversation(Base):
    __tablename__ = "conversations"
    user_id: str = mapped_column(ForeignKey("users.id"))
    events: List[ConversationEvent] = relationship("ConversationEvent", default=[])
    id: str = mapped_column(default=uuid4, primary_key=True, nullable=False)

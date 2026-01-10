from typing import List, Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, relationship, Mapped

from src.db.models.base import Base
from src.db.models.user import User


class Conversation(Base):
    __tablename__ = "conversations"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    user: Mapped[User] = relationship(back_populates="conversations")
    id: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    messages: Mapped[List["ConversationMessage"]] = relationship(
        back_populates="conversation", default_factory=list
    )


class ConversationMessage(Base):
    __tablename__ = "conversations_messages"
    id: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id"))
    conversation: Mapped[Optional[Conversation]] = relationship(
        back_populates="messages", default=None
    )

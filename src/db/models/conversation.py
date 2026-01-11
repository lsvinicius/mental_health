import datetime
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import ForeignKey, DateTime, JSON
from sqlalchemy.orm import mapped_column, relationship, Mapped

from src.db.models.base import Base
from src.db.models.user import User


class Conversation(Base):
    __tablename__ = "conversations"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    user: Mapped[User] = relationship(back_populates="conversations")
    id: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    status: Mapped[Optional[str]] = mapped_column(nullable=True, default=None)
    messages: Mapped[List["ConversationMessage"]] = relationship(
        back_populates="conversation", default_factory=list
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
        nullable=False,
    )

    def to_text(self) -> str:
        lines = [
            f"Name: {self.user.name}\tEmail: {self.user.email}\n",
            "Messages:\n\n",
            "=========BEGIN=============\n",
        ]
        self.messages.sort(key=lambda m: m.version)
        for message in self.messages:
            lines.append(f"At: {message.created_at}\nText: {message.text}\n\n")
        lines.append("=========END===========\n")
        return "\n".join(lines)


class ConversationMessage(Base):
    __tablename__ = "conversations_messages"
    id: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id"))
    text: Mapped[str] = mapped_column(nullable=False)
    sender: Mapped[str] = mapped_column(ForeignKey("users.email"))
    version: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    conversation: Mapped[Optional[Conversation]] = relationship(
        back_populates="messages", default=None
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
        nullable=False,
    )


class ConversationRiskAnalysis(Base):
    __tablename__ = "conversation_analyses"
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id"))
    analysis: Mapped[dict] = mapped_column(JSON)
    detected_risk: Mapped[bool] = mapped_column()
    id: Mapped[str] = mapped_column(
        primary_key=True, default_factory=lambda: str(uuid4())
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
        nullable=False,
    )

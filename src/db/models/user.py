from uuid import uuid4

from sqlalchemy.orm import mapped_column, relationship

from src.db.models.base import Base


class User(Base):
    __tablename__ = "users"
    email: str = mapped_column(unique=True)
    name: str = mapped_column()
    conversations: list = relationship(
        "Conversation", back_populates="users", default_factory=list
    )
    id: str = mapped_column(primary_key=True, default_factory=uuid4)

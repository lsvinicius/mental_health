from uuid import uuid4

from sqlalchemy.orm import mapped_column

from src.db.models.base import Base


class User(Base):
    __tablename__ = "users"
    email: str = mapped_column(unique=True)
    name: str = mapped_column()
    id: str = mapped_column(primary_key=True, default_factory=lambda: str(uuid4()))

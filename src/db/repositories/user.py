from src.db.models.user import User
from src.db.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session, User)

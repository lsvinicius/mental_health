from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.conversation import Conversation
from src.db.repositories.base import BaseRepository


class ConversationRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Conversation)

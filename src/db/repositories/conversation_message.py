from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.conversation import ConversationMessage
from src.db.repositories.base import BaseRepository


class ConversationMessageRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ConversationMessage)

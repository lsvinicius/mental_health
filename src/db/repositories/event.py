from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.event import ConversationEvent
from src.db.repositories.base import BaseRepository


class ConversationEventRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ConversationEvent)

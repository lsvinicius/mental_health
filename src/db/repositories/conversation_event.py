from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.event import ConversationEvent
from src.db.repositories.base import BaseRepository


class ConversationEventRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ConversationEvent)

    async def get_all_conversation_events(
        self, conversation_id: str
    ) -> List[ConversationEvent]:
        stmt = (
            select(ConversationEvent)
            .where(ConversationEvent.conversation_id == conversation_id)
            .order_by(ConversationEvent.version)
        )
        results = await self._session.execute(stmt)
        return list(results.scalars().all())

import datetime
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.conversation_outbox import ConversationOutbox
from src.db.repositories.base import BaseRepository


class ConversationOutboxRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ConversationOutbox)

    async def all_unprocessed(self) -> List[ConversationOutbox]:
        results = await self._session.execute(
            select(ConversationOutbox)
            .where(ConversationOutbox.is_processed == False)
            .order_by(ConversationOutbox.created_at)
        )
        results = list(results.scalars().all())
        for r in results:
            await self._session.refresh(r, attribute_names=["event"])
        return results

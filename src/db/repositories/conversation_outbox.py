import datetime
from typing import List

from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.conversation_outbox import ConversationOutbox
from src.db.repositories.base import BaseRepository


class ConversationOutboxRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ConversationOutbox)

    async def update(self, outbox: ConversationOutbox) -> ConversationOutbox:
        if outbox.updated_at is None:
            outbox.updated_at = datetime.datetime.now(datetime.timezone.utc)
        stmt = (
            update(self._model)
            .where(ConversationOutbox.id == outbox.id)
            .values(is_processed=outbox.is_processed, updated_at=outbox.updated_at)
        )
        await self._session.execute(stmt)
        return outbox

    async def all_unprocessed(self) -> List[ConversationOutbox]:
        results = await self._session.execute(
            select(ConversationOutbox)
            .where(ConversationOutbox.is_processed == False)
            .order_by(ConversationOutbox.created_at)
        )
        return list(results.scalars().all())

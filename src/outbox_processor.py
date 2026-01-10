import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repositories.conversation_outbox import ConversationOutboxRepository


class OutboxProcessor:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._outbox_repository = ConversationOutboxRepository(session)

    async def process(self, forever: bool = True, interval: int = 5):
        if forever:
            while True:
                await self._process()
                await asyncio.sleep(interval)
        else:
            await self._process()

    async def _process(self):
        outboxes = await self._outbox_repository.all_unprocessed()
        for outbox in outboxes:
            outbox.conversation_id

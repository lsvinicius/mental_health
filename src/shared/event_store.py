from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.event import ConversationEvent
from src.db.repositories.event import ConversationEventRepository


class EventStore:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._conversation_event_repository = ConversationEventRepository(session)

    async def append_event(self, event: ConversationEvent):
        await self._conversation_event_repository.save(event)

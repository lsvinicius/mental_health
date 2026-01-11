from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.event import ConversationEvent
from src.db.models.conversation_outbox import ConversationOutbox
from src.db.repositories.conversation_event import ConversationEventRepository
from src.db.repositories.conversation_outbox import ConversationOutboxRepository


class EventStore:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._conversation_event_repository = ConversationEventRepository(session)
        self._outbox_repository = ConversationOutboxRepository(session)

    async def append_event(self, event: ConversationEvent) -> None:
        await self._conversation_event_repository.save(event)
        await self._outbox_repository.save(
            ConversationOutbox(event_id=event.id, event=event)
        )

    async def retrieve_events(self, conversation_id: str) -> List[ConversationEvent]:
        return await self._conversation_event_repository.get_all_conversation_events(
            conversation_id
        )

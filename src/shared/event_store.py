from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.event import ConversationEvent
from src.db.models.conversationoutbox import ConversationOutbox
from src.db.repositories.event import ConversationEventRepository
from src.db.repositories.outbox import ConversationOutboxRepository


class EventStore:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._conversation_event_repository = ConversationEventRepository(session)
        self._outbox_repository = ConversationOutboxRepository(session)

    async def append_conversation_event(self, event: ConversationEvent) -> None:
        await self._conversation_event_repository.save(event)
        await self._outbox_repository.save(
            ConversationOutbox(
                payload=event.payload, conversation_id=event.conversation_id
            )
        )

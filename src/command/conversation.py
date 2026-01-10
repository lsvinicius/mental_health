from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.aggregates.conversation import ConversationAggregate
from src.db.models.conversation import Conversation
from src.db.models.event import ConversationEvent, EventType
from src.db.repositories.conversation import ConversationRepository
from src.db.repositories.event import ConversationEventRepository
from src.shared.event_store import EventStore


class ConversationCommandHandler:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._event_store = EventStore(session)
        self._conversation_repository = ConversationRepository(session)
        self._conversation_event_repository = ConversationEventRepository(session)

    async def start_conversation(self, user_id: str) -> str:
        """Start a new conversation."""
        async with self._session.begin():
            conversation = Conversation(user_id=user_id)
            await self._conversation_repository.save(conversation)
            await self._handle_command(
                conversation.id, event_type=EventType.CONVERSATION_STARTED
            )
        return conversation.id

    async def new_message(self, conversation_id: str, text: str, sender: str) -> bool:
        """Add a new message to the conversation."""
        async with self._session.begin():
            await self._handle_command(
                conversation_id,
                EventType.NEW_MESSAGE,
                payload={"sender": sender, "text": text},
            )
        return True

    async def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a message from the conversation."""
        async with self._session.begin():
            await self._handle_command(conversation_id, EventType.CONVERSATION_DELETED)
        return True

    async def _handle_command(
        self,
        conversation_id: str,
        event_type: EventType,
        payload: Optional[dict] = None,
    ) -> None:
        events = await self._conversation_event_repository.get_all_conversation_events(
            conversation_id
        )
        event = ConversationEvent(
            conversation_id=conversation_id,
            type=event_type,
            payload=payload,
        )
        events.append(event)
        aggregate = ConversationAggregate(conversation_id=conversation_id)
        aggregate.apply_events(events)
        await self._event_store.append_conversation_event(event)

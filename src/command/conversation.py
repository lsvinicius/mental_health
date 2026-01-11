from typing import Optional
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from src.aggregates.conversation import ConversationAggregate
from src.db.models.event import ConversationEvent, EventType
from src.shared.event_store import EventStore


class ConversationCommandHandler:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._event_store = EventStore(session)

    async def start_conversation(self, user_id: str) -> str:
        """Start a new conversation."""
        conversation_id = str(uuid4())
        await self._handle_command(
            conversation_id,
            event_type=EventType.CONVERSATION_STARTED,
            payload={"user_id": user_id},
        )
        return conversation_id

    async def new_message(self, conversation_id: str, text: str, sender: str) -> str:
        """Add a new message to the conversation."""
        message_id = str(uuid4())
        await self._handle_command(
            conversation_id,
            EventType.NEW_MESSAGE,
            payload={"sender": sender, "text": text, "message_id": message_id},
        )
        return message_id

    async def delete_conversation(self, user_id: str, conversation_id: str) -> str:
        """Delete a message from the conversation."""
        await self._handle_command(
            conversation_id,
            EventType.CONVERSATION_DELETED,
            payload={"user_id": user_id},
        )
        return conversation_id

    async def _handle_command(
        self,
        conversation_id: str,
        event_type: EventType,
        payload: Optional[dict] = None,
    ) -> None:
        async with self._session.begin():
            events = await self._event_store.retrieve_events(conversation_id)
            aggregate = ConversationAggregate(conversation_id=conversation_id)
            aggregate.apply_events(events)

            event = ConversationEvent(
                conversation_id=conversation_id,
                type=event_type,
                payload=payload,
                version=aggregate.version + 1,
            )
            aggregate.apply(event)
            await self._event_store.append_event(event)

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.conversation import Conversation
from src.db.models.event import ConversationEvent, EventType
from src.db.repositories.conversation import ConversationRepository
from src.shared.event_store import EventStore


class ConversationCommandHandler:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._event_store = EventStore(session)
        self._conversation_repository = ConversationRepository(session)

    async def start_conversation(self, user_id: str) -> str:
        """Start a new conversation."""
        conversation = Conversation(user_id=user_id)
        async with self._session:
            await self._conversation_repository.save(conversation)
            new_conversation_event = ConversationEvent(
                type=EventType.CONVERSATION_STARTED, conversation_id=conversation.id
            )
            await self._event_store.append_event(new_conversation_event)
        return conversation.id

    async def new_message(self, conversation_id: str, text: str, sender: str) -> str:
        """Add a new message to the conversation."""
        async with self._session:
            new_message_event = ConversationEvent(
                conversation_id=conversation_id,
                type=EventType.NEW_MESSAGE,
                payload={"sender": sender, "text": text},
            )
            await self._event_store.append_event(new_message_event)
            return new_message_event.id

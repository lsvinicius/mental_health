from sqlalchemy.ext.asyncio import AsyncSession

from src.aggregates.conversation import ConversationStatus
from src.db.models.conversation import Conversation, ConversationMessage
from src.db.models.conversation_outbox import ConversationOutbox
from src.db.models.event import EventType
from src.db.repositories.conversation import ConversationRepository
from src.db.repositories.conversation_message import ConversationMessageRepository
from src.db.repositories.user import UserRepository


class ConversationProjector:

    def __init__(self, session: AsyncSession):
        self._session = session
        self._conversation_repository = ConversationRepository(session)
        self._conversation_messages_repository = ConversationMessageRepository(session)
        self._user_repository = UserRepository(session)

    async def project(self, conversation_outbox: ConversationOutbox):
        event = conversation_outbox.event
        if event.type == EventType.CONVERSATION_STARTED:
            user_id = event.payload["user_id"]
            user = await self._user_repository.get(user_id)
            conversation = Conversation(
                user_id=event.payload["user_id"],
                id=event.conversation_id,
                user=user,
                status=ConversationStatus.ACTIVE,
            )
            await self._conversation_repository.save(conversation)
        elif event.type == EventType.NEW_MESSAGE:
            message_id = event.payload["message_id"]
            message = ConversationMessage(
                id=message_id,
                conversation_id=event.conversation_id,
                text=event.payload["text"],
                sender=event.payload["sender"],
                version=event.version,
            )
            await self._conversation_messages_repository.save(message)
        elif event.type == EventType.CONVERSATION_DELETED:
            await self._conversation_repository.update(
                event.conversation_id, status=ConversationStatus.INACTIVE
            )

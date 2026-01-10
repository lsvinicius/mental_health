from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repositories.conversation_event import ConversationEventRepository


class ConversationQueryHandler:

    def __init__(self, session: AsyncSession):
        self._conversation_event_repository = ConversationEventRepository(session)

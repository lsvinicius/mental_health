from sqlalchemy.ext.asyncio import AsyncSession

from src.aggregates.conversation import ConversationAggregate
from src.db.repositories.event import ConversationEventRepository


class ConversationQueryHandler:

    def __init__(self, session: AsyncSession):
        self._conversation_event_repository = ConversationEventRepository(session)

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.conversation import Conversation
from src.db.repositories.conversation import ConversationRepository


class ConversationQueryHandler:

    def __init__(self, session: AsyncSession):
        self._conversation_repository = ConversationRepository(session)

    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        return await self._conversation_repository.get(conversation_id)

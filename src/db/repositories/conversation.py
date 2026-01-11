from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models.conversation import Conversation
from src.db.repositories.base import BaseRepository


class ConversationRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Conversation)

    async def get(self, id_: Any) -> Optional[Conversation]:
        if not hasattr(self._model, "id"):
            raise ValueError(f"Need id in model {self._model}")
        result = await self._session.execute(
            select(self._model)
            .where(Conversation.id == id_)
            .options(
                selectinload(Conversation.messages), selectinload(Conversation.user)
            )
        )
        return result.scalar()

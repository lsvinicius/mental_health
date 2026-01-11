from typing import List

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.conversation import ConversationRiskAnalysis
from src.db.repositories.base import BaseRepository


class ConversationRiskAnalysisRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ConversationRiskAnalysis)

    async def all(
        self, conversation_id: str, return_only_risky_ones: bool = True
    ) -> List[ConversationRiskAnalysis]:
        if return_only_risky_ones:
            stmt = (
                select(ConversationRiskAnalysis)
                .where(
                    and_(
                        ConversationRiskAnalysis.conversation_id == conversation_id,
                        ConversationRiskAnalysis.detected_risk.is_(True),
                    )
                )
                .order_by(ConversationRiskAnalysis.created_at)
            )
        else:
            stmt = (
                select(ConversationRiskAnalysis)
                .where(ConversationRiskAnalysis.conversation_id == conversation_id)
                .order_by(ConversationRiskAnalysis.created_at)
            )
        results = await self._session.execute(stmt)
        return list(results.scalars().all())

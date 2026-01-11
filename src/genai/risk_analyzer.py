from pathlib import Path
from typing import Optional

import yaml
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.conversation import ConversationRiskAnalysis
from src.db.repositories.conversation import ConversationRepository
from src.db.repositories.conversation_analysis import ConversationRiskAnalysisRepository
from src.genai.risk_analyzer_clients.base import AIAnalyzerClient


class RiskAnalyzer:
    def __init__(
        self,
        session: AsyncSession,
        ai_client: AIAnalyzerClient,
        prompt_path: Optional[str] = None,
    ):
        self._session = session
        self._ai_client = ai_client
        self._conversation_repository = ConversationRepository(session)
        self._conversation_risk_repository = ConversationRiskAnalysisRepository(session)
        self._prompt = _load_config(
            prompt_path or str(Path.cwd() / "prompts" / "risk_analyzer.yaml")
        )

    async def analyze(self, conversation_id: str) -> ConversationRiskAnalysis:
        async with self._session.begin():
            conversation = await self._conversation_repository.get(conversation_id)
            if not conversation:
                raise ValueError(f"No conversation with id {conversation_id}")
            formatted_prompt = yaml.dump(self._prompt, allow_unicode=True).replace(
                "{{conversation_history}}", conversation.to_text()
            )
            ai_analysis = await self._ai_client.get_risk_assessment(
                prompt=formatted_prompt
            )
            risk = ConversationRiskAnalysis(
                conversation_id=conversation_id,
                analysis=ai_analysis.model_dump(),
                detected_risk=ai_analysis.risk_found or False,
            )
            await self._conversation_risk_repository.save(risk)
            return risk


def _load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

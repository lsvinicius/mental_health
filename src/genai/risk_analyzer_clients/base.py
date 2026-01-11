import asyncio
import logging
from abc import ABC, abstractmethod
from typing import List, Optional

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class UnableToAnalyzeError(Exception):
    pass


class AIAnalysis(BaseModel):
    risk_found: Optional[bool] = None
    risk_level: Optional[str] = None
    detected_indicators: Optional[List[str]] = None
    clinical_reasoning: Optional[str] = None
    recommended_action: Optional[str] = None


class AIAnalyzerClient(ABC):

    def __init__(self, **kwargs):
        self._kwargs = kwargs

    async def get_risk_assessment(self, prompt: str, retries: int = 5) -> AIAnalysis:
        chance = 0
        wait_for = 3
        while chance < retries:
            try:
                return await self._get_risk_assessment(prompt)
            except Exception as e:
                logger.error(
                    f"Failed to get risk assessment for prompt {prompt} due to error {e}"
                )
                chance += 1
            await asyncio.sleep(wait_for)
            wait_for = wait_for**chance
        raise UnableToAnalyzeError(f"Failed to get risk assessment for prompt {prompt}")

    @abstractmethod
    async def _get_risk_assessment(self, prompt: str) -> AIAnalysis:
        pass

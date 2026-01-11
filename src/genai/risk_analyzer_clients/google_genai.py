import json

from google import genai

from src.genai.risk_analyzer_clients.base import AIAnalyzerClient, AIAnalysis


class GoogleGenAIClient(AIAnalyzerClient):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._client = genai.Client(api_key=self._kwargs["api_key"])
        self._model_id = self._kwargs.get("model_id", "gemini-2.0-flash")

    async def _get_risk_assessment(self, prompt: str) -> AIAnalysis:
        response = self._client.models.generate_content(
            model=self._model_id, contents=prompt
        )
        return AIAnalysis(**json.loads(response.text))

from enum import Enum

from src.genai.risk_analyzer_clients.base import AIAnalyzerClient
from src.genai.risk_analyzer_clients.google_genai import GoogleGenAIClient


class AnalyzerClientProvider(str, Enum):
    google_genai = "google_genai"


def create_analyzer_client(
    provider: AnalyzerClientProvider, **kwargs
) -> AIAnalyzerClient:
    if provider == AnalyzerClientProvider.google_genai:
        return GoogleGenAIClient(**kwargs)
    else:
        raise ValueError(f"Unsupported analyzer client {provider}")

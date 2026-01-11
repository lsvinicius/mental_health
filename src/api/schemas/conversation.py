from typing import Optional

from pydantic import BaseModel


# Request Models
class StartConversationRequest(BaseModel):
    user_id: str


class SendMessageRequest(BaseModel):
    text: str
    sender: str


class DeleteConversationRequest(BaseModel):
    user_id: str


class GetConversationRequest(BaseModel):
    timezone: str = "America/Sao_Paulo"


class AnalyzeConversationRiskRequest(BaseModel):
    model: str = "gemini-2.0-flash"

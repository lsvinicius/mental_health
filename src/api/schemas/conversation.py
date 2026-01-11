from pydantic import BaseModel


class SendMessageRequest(BaseModel):
    text: str
    sender: str


class AnalyzeConversationRiskRequest(BaseModel):
    model: str = "gemini-2.0-flash"

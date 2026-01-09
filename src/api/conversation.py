from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.api.dependencies import ConversationCommandHandlerDependency

router = APIRouter()


# Request Models
class StartConversationRequest(BaseModel):
    user_id: str


class SendMessageRequest(BaseModel):
    text: str
    sender: str


# Routes
@router.post("/conversations", status_code=201)
async def start_conversation(
    request: StartConversationRequest,
    command_handler: ConversationCommandHandlerDependency,
):
    """Start a new conversation."""
    conversation_id = await command_handler.start_conversation(request.user_id)
    return {
        "conversation_id": conversation_id,
        "message": "Conversation started successfully",
    }


@router.post("/conversations/{conversation_id}/messages", status_code=201)
async def new_message(
    conversation_id: str,
    request: SendMessageRequest,
    command_handler: ConversationCommandHandlerDependency,
):
    """Send messages to a conversation."""
    try:
        message_id = await command_handler.new_message(
            conversation_id, request.text, request.sender
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "message_id": message_id,
        "conversation_id": conversation_id,
    }


# @router.get("/conversations/{conversation_id}")
# async def get_conversation(conversation_id: UUID):
#     """Busca informações da conversa"""
#     summary = await conversation_queries.get_conversation_summary(conversation_id)
#     if not summary:
#         raise HTTPException(status_code=404, detail="Conversation not found")
#
#     timeline = await conversation_queries.get_risk_timeline(conversation_id)
#
#     return {
#         "summary": summary,
#         "risk_timeline": timeline
#     }
#
#
# @router.get("/alerts")
# async def get_alerts(status: Optional[str] = None):
#     """Lista alertas ativos (dashboard do profissional)"""
#     alerts = await conversation_queries.get_active_alerts(status)
#     return {
#         "alerts": alerts,
#         "count": len(alerts)
#     }


@router.get("/health")
async def health_check():
    """Health check"""
    return {"status": "healthy"}

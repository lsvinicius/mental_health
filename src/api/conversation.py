from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException
from src.api.dependencies import (
    ConversationCommandHandlerDependency,
    ConversationQueryHandlerDependency,
    ConversationRiskAnalysisRepositoryDependency,
)
from src.api.schemas.conversation import (
    SendMessageRequest,
    GetConversationRequest,
)
from src.dtos.conversation import ConversationDTO, ConversationRiskAnalysisDTO

router = APIRouter(prefix="/{user_id}")


# Routes
@router.post("/conversations", status_code=201)
async def start_conversation(
    user_id: str,
    command_handler: ConversationCommandHandlerDependency,
):
    """Start a new conversation."""
    conversation_id = await command_handler.start_conversation(user_id)
    return {
        "conversation_id": conversation_id,
    }


@router.delete("/conversations/{conversation_id}", status_code=201)
async def delete_conversation(
    conversation_id: str,
    user_id: str,
    command_handler: ConversationCommandHandlerDependency,
):
    """Send messages to a conversation."""
    try:
        await command_handler.delete_conversation(user_id, conversation_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "conversation_id": conversation_id,
    }


@router.post("/conversations/{conversation_id}/messages", status_code=201)
async def new_message(
    conversation_id: str,
    user_id: str,
    request: SendMessageRequest,
    command_handler: ConversationCommandHandlerDependency,
):
    """Send messages to a conversation."""
    try:
        message_id = await command_handler.new_message(
            user_id, conversation_id, request.text, request.sender
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "message_id": message_id,
    }


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    user_id: str,
    conversation_id: str,
    payload: GetConversationRequest,
    query_handler: ConversationQueryHandlerDependency,
):
    """Get conversation."""
    try:
        tz = ZoneInfo(payload.timezone)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    conversation = await query_handler.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conversation.user_id != user_id:
        raise HTTPException(
            status_code=403, detail="Forbidden: Conversation does not belong to user"
        )

    dto = ConversationDTO.model_validate(conversation)
    return dto.to_timezone(tz)


@router.get("/conversations/{conversation_id}/risk_analyzes")
async def get_conversation_analyses_risk(
    user_id: str,
    conversation_id: str,
    query_handler: ConversationQueryHandlerDependency,
    conversation_risk_analysis_repository: ConversationRiskAnalysisRepositoryDependency,
    return_risk_ones_only: bool = True,
):
    """Get risk analyzes."""
    conversation = await query_handler.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conversation.user_id != user_id:
        raise HTTPException(
            status_code=403, detail="Forbidden: Conversation does not belong to user"
        )

    risk_analyses = await conversation_risk_analysis_repository.all(
        conversation_id, return_risk_ones_only
    )
    return {
        "risk_analyses": [
            ConversationRiskAnalysisDTO.model_validate(risk_analysis)
            for risk_analysis in risk_analyses
        ]
    }

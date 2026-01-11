from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException
from src.api.dependencies import (
    ConversationCommandHandlerDependency,
    ConversationQueryHandlerDependency,
    RiskAnalyzerCreatorDependency,
    ConversationRiskAnalysisRepositoryDependency,
)
from src.api.schemas.conversation import (
    StartConversationRequest,
    DeleteConversationRequest,
    SendMessageRequest,
    GetConversationRequest,
    AnalyzeConversationRiskRequest,
)
from src.dtos.conversation import ConversationDTO, ConversationRiskAnalysisDTO

router = APIRouter()


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
    }


@router.delete("/conversations/{conversation_id}", status_code=201)
async def delete_conversation(
    conversation_id: str,
    request: DeleteConversationRequest,
    command_handler: ConversationCommandHandlerDependency,
):
    """Send messages to a conversation."""
    try:
        await command_handler.delete_conversation(request.user_id, conversation_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "conversation_id": conversation_id,
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
    }


@router.get("/conversations/{conversation_id}")
async def get_conversation(
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

    dto = ConversationDTO.model_validate(conversation)
    return dto.to_timezone(tz)


@router.post("/conversations/{conversation_id}/analyze_risk")
async def analyze_risk(
    conversation_id: str,
    payload: AnalyzeConversationRiskRequest,
    risk_analyzer_creator: RiskAnalyzerCreatorDependency,
):
    """Analyze risk."""
    risk_analyzer = risk_analyzer_creator(payload.model)
    try:
        risk_analysis = await risk_analyzer.analyze(conversation_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return ConversationRiskAnalysisDTO.model_validate(risk_analysis)


@router.get("/conversations/{conversation_id}/risk_analyzes")
async def get_conversation_analyses_risk(
    conversation_id: str,
    conversation_risk_analysis_repository: ConversationRiskAnalysisRepositoryDependency,
    return_risk_ones_only: bool = True,
):
    """Get risk analyzes."""
    risk_analyses = await conversation_risk_analysis_repository.get_all(
        conversation_id, return_risk_ones_only
    )
    return {
        "risk_analyses": [
            ConversationRiskAnalysisDTO.model_validate(risk_analysis)
            for risk_analysis in risk_analyses
        ]
    }

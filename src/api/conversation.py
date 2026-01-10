from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.api.dependencies import (
    ConversationCommandHandlerDependency,
    ConversationQueryHandlerDependency,
)

# from src.db.models.conversation import Conversation

router = APIRouter()


# Request Models
class StartConversationRequest(BaseModel):
    user_id: str


class SendMessageRequest(BaseModel):
    text: str
    sender: str


class DeleteConversationRequest(BaseModel):
    user_id: str


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
    conversation_id: str, command_handler: ConversationQueryHandlerDependency
):
    """Get conversation."""
    # aggregate = await command_handler.get_conversation_aggregate(conversation_id)

    return {}


@router.get("/health")
async def health_check():
    """Health check"""
    return {"status": "healthy"}

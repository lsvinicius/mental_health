import asyncio
import json
from unittest.mock import Mock

import pytest

from src.aggregates.conversation import ConversationStatus
from src.db.repositories.conversation import ConversationRepository
from src.db.repositories.conversation_analysis import ConversationRiskAnalysisRepository
from src.db.repositories.conversation_message import ConversationMessageRepository
from src.db.repositories.conversation_outbox import ConversationOutboxRepository
from src.outbox_processor import OutboxProcessor


@pytest.mark.asyncio(loop_scope="session")
async def test_outbox_process_and_project(
    db_session, create_user, create_conversation, create_message, base_url
):
    # given
    user_id = (await create_user("vini", "vini@vini.com"))["user_id"]
    conversation_id = (await create_conversation(user_id))["conversation_id"]
    await create_message(user_id, conversation_id, "hi", "vini@vini.com")

    processor = OutboxProcessor(db_session, base_url)

    # when
    conversations = await processor._process()

    # then - verify outbox entries were processed
    outbox_repository = ConversationOutboxRepository(db_session)
    outboxes = await outbox_repository.all()
    assert len(outboxes) == 2
    for outbox in outboxes:
        assert outbox.is_processed is True
        assert outbox.created_at is not None
        assert outbox.updated_at is not None
    assert conversations == [conversation_id]

    # then - verify read model (Conversation) was created
    conversation_repository = ConversationRepository(db_session)
    conversation = await conversation_repository.get(conversation_id)
    assert conversation is not None
    assert conversation.id == conversation_id
    assert conversation.user_id == user_id
    assert conversation.status == ConversationStatus.ACTIVE
    assert conversation.created_at is not None

    # then - verify read model (ConversationMessage) was created
    message_repository = ConversationMessageRepository(db_session)
    messages = await message_repository.all()
    assert len(messages) == 1
    message = messages[0]
    assert message.conversation_id == conversation_id
    assert message.text == "hi"
    assert message.sender == "vini@vini.com"
    assert (
        message.version == 2
    )  # Version 1 is CONVERSATION_STARTED, version 2 is NEW_MESSAGE
    assert message.created_at is not None


@pytest.mark.asyncio(loop_scope="session")
async def test_outbox_process_and_project_and_request_risk_analysis(
    db_session, create_user, create_conversation, create_message, base_url, monkeypatch
):
    # given
    user_id = (await create_user("vini", "vini@vini.com"))["user_id"]
    conversation_id = (await create_conversation(user_id))["conversation_id"]
    await create_message(user_id, conversation_id, "hi", "vini@vini.com")
    processor = OutboxProcessor(db_session, base_url)
    analysis = """
    {
    "clinical_reasoning": "The conversation contains only a simple greeting and does not provide any indicators of self-harm or suicidal ideation, planning, intent, or history.",
    "detected_indicators": [],
    "recommended_action": null,
    "risk_found": false,
    "risk_level": null
     }
    """
    mock = Mock()
    mock.models.generate_content.return_value = Mock(text=analysis)
    genai_client = Mock(return_value=mock)
    monkeypatch.setattr(
        "src.genai.risk_analyzer_clients.google_genai.genai.Client", genai_client
    )

    # when
    await processor.process_and_send_to_risk_analyzer(forever=False)

    # give some time for event loop to process request before we validate
    await asyncio.sleep(3)

    # then
    risk_analysis_repository = ConversationRiskAnalysisRepository(db_session)
    analyses = await risk_analysis_repository.all(
        conversation_id, return_only_risky_ones=False
    )

    assert len(analyses) == 1
    assert analyses[0].conversation_id == conversation_id
    assert analyses[0].analysis == json.loads(analysis)
    assert analyses[0].detected_risk == False
    assert analyses[0].created_at is not None


@pytest.mark.asyncio(loop_scope="session")
async def test_outbox_process_and_project_and_request_risk_analysis_for_risky_message(
    db_session, create_user, create_conversation, create_message, base_url, monkeypatch
):
    # given
    user_id = (await create_user("anonymous", "anonymous@email.com"))["user_id"]
    conversation_id = (await create_conversation(user_id))["conversation_id"]
    await create_message(
        user_id, conversation_id, "I want to die", "anonymous@email.com"
    )
    processor = OutboxProcessor(db_session, base_url)
    analysis = """
    {
      "risk_found": true,
      "risk_level": "high",
      "detected_indicators": ["plan", "intent"],
      "clinical_reasoning": "The user mentioned possessing means and a specific date for the act.",
      "recommended_action": "immediate intervention"
    }
    """
    mock = Mock()
    mock.models.generate_content.return_value = Mock(text=analysis)
    genai_client = Mock(return_value=mock)
    monkeypatch.setattr(
        "src.genai.risk_analyzer_clients.google_genai.genai.Client", genai_client
    )

    # when
    await processor.process_and_send_to_risk_analyzer(forever=False)

    # give some time for event loop to process request before we validate
    await asyncio.sleep(3)

    # then
    risk_analysis_repository = ConversationRiskAnalysisRepository(db_session)
    analyses = await risk_analysis_repository.all(
        conversation_id, return_only_risky_ones=False
    )

    assert len(analyses) == 1
    assert analyses[0].conversation_id == conversation_id
    assert analyses[0].analysis == json.loads(analysis)
    assert analyses[0].detected_risk == True
    assert analyses[0].created_at is not None

import pytest

from src.aggregates.conversation import ConversationStatus
from src.db.repositories.conversation import ConversationRepository
from src.db.repositories.conversation_message import ConversationMessageRepository
from src.db.repositories.conversation_outbox import ConversationOutboxRepository
from src.outbox_processor import OutboxProcessor


@pytest.mark.asyncio(loop_scope="session")
async def test_outbox_process_and_project(
    db_session, client, create_user, create_conversation, create_message
):
    # given
    user_id = (await create_user("vini", "vini@vini.com"))["user_id"]
    conversation_id = (await create_conversation(user_id))["conversation_id"]
    await create_message(user_id, conversation_id, "hi", "vini@vini.com")

    processor = OutboxProcessor(db_session)

    # when
    await processor._process()

    # then - verify outbox entries were processed
    outbox_repository = ConversationOutboxRepository(db_session)
    outboxes = await outbox_repository.all()
    assert len(outboxes) == 2
    for outbox in outboxes:
        assert outbox.is_processed is True
        assert outbox.created_at is not None
        assert outbox.updated_at is not None

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

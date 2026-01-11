import pytest

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

    # then
    outbox_repository = ConversationOutboxRepository(db_session)
    outboxes = await outbox_repository.all()
    assert len(outboxes) == 2
    for outbox in outboxes:
        assert outbox.is_processed is True
        assert outbox.created_at is not None
        assert outbox.updated_at is not None

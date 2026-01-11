import pytest

from src.api.schemas.conversation import SendMessageRequest
from src.db.models.event import EventType
from src.db.repositories.conversation_event import ConversationEventRepository
from src.db.repositories.conversation_outbox import ConversationOutboxRepository


@pytest.mark.asyncio(loop_scope="session")
async def test_create_conversation(db_session, client, create_user):
    # given
    conversation_event_repository = ConversationEventRepository(db_session)
    outbox_repository = ConversationOutboxRepository(db_session)
    result = await create_user("vini", "vini@vini.com")
    user_id = result["user_id"]

    # when
    response = await client.post(f"/api/v1/{user_id}/conversations")

    # then
    assert response.status_code == 201
    conversation_id = response.json()["conversation_id"]
    events = await conversation_event_repository.all()

    assert len(events) == 1
    assert events[0].conversation_id == conversation_id
    assert events[0].type == EventType.CONVERSATION_STARTED
    assert events[0].version == 1
    assert events[0].payload == {"user_id": user_id}
    assert events[0].created_at is not None
    assert events[0].id is not None

    outbox = await outbox_repository.all()
    assert len(outbox) == 1
    assert outbox[0].event_id == events[0].id
    assert outbox[0].is_processed is False
    assert outbox[0].created_at is not None
    assert outbox[0].updated_at is None


@pytest.mark.asyncio(loop_scope="session")
async def test_send_new_message(db_session, client, create_user, create_conversation):
    # given
    conversation_event_repository = ConversationEventRepository(db_session)
    outbox_repository = ConversationOutboxRepository(db_session)
    result = await create_user("vini", "vini@vini.com")
    user_id = result["user_id"]
    result = await create_conversation(user_id)
    conversation_id = result["conversation_id"]

    # when
    payload = SendMessageRequest(text="hello", sender="vini")
    response = await client.post(
        f"/api/v1/{user_id}/conversations/{conversation_id}/messages",
        json=payload.model_dump(),
    )
    message_id = response.json()["message_id"]

    # then
    assert response.status_code == 201
    events = await conversation_event_repository.all()

    assert len(events) == 2
    assert events[-1].conversation_id == conversation_id
    assert events[-1].type == EventType.NEW_MESSAGE
    assert events[-1].version == 2
    assert events[-1].payload == {
        "text": "hello",
        "sender": "vini",
        "message_id": message_id,
    }
    assert events[-1].created_at is not None
    assert events[-1].id is not None

    outbox = await outbox_repository.all()
    assert len(outbox) == 2
    assert outbox[-1].event_id == events[-1].id
    assert outbox[-1].is_processed is False
    assert outbox[-1].created_at is not None
    assert outbox[-1].updated_at is None


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_conversation(
    db_session, client, create_user, create_conversation, create_message
):
    # given
    conversation_event_repository = ConversationEventRepository(db_session)
    outbox_repository = ConversationOutboxRepository(db_session)
    user_id = (await create_user("vini", "vini@vini.com"))["user_id"]
    conversation_id = (await create_conversation(user_id))["conversation_id"]
    await create_message(user_id, conversation_id, "hi", "vini")

    # when
    response = await client.delete(f"/api/v1/{user_id}/conversations/{conversation_id}")

    # then
    assert response.status_code == 201
    assert response.json()["conversation_id"] == conversation_id
    events = await conversation_event_repository.all()

    assert len(events) == 3
    assert events[-1].conversation_id == conversation_id
    assert events[-1].type == EventType.CONVERSATION_DELETED
    assert events[-1].version == 3
    assert events[-1].payload == {"conversation_id": conversation_id}
    assert events[-1].created_at is not None
    assert events[-1].id is not None

    outbox = await outbox_repository.all()
    assert len(outbox) == 3
    assert outbox[-1].event_id == events[-1].id
    assert outbox[-1].is_processed is False
    assert outbox[-1].created_at is not None
    assert outbox[-1].updated_at is None

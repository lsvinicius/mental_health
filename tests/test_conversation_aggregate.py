import datetime
from uuid import uuid4

import pytest

from src.aggregates.conversation import ConversationAggregate, ConversationStatus
from src.db.models.event import ConversationEvent, EventType


class TestConversationAggregate:
    def test_start_conversation(self):
        # given
        conversation_id = str(uuid4())
        user_id = str(uuid4())
        aggregate = ConversationAggregate(conversation_id, user_id)

        # when
        event = ConversationEvent(
            conversation_id=conversation_id,
            user_id=user_id,
            type=EventType.CONVERSATION_STARTED,
            payload={"user_id": user_id},
            version=1,
        )
        aggregate.apply(event)

        # then
        assert aggregate.status == ConversationStatus.ACTIVE
        assert aggregate.version == 1

    def test_cannot_start_conversation_twice(self):
        # given
        conversation_id = str(uuid4())
        user_id = str(uuid4())
        aggregate = ConversationAggregate(conversation_id, user_id)

        event1 = ConversationEvent(
            conversation_id=conversation_id,
            user_id=user_id,
            type=EventType.CONVERSATION_STARTED,
            payload={"user_id": user_id},
            version=1,
        )
        aggregate.apply(event1)

        # when/then
        event2 = ConversationEvent(
            conversation_id=conversation_id,
            user_id=user_id,
            type=EventType.CONVERSATION_STARTED,
            payload={"user_id": user_id},
            version=2,
        )

        with pytest.raises(ValueError, match="Cannot start conversation with status"):
            aggregate.apply(event2)

    def test_add_message_to_active_conversation(self):
        # given
        conversation_id = str(uuid4())
        user_id = str(uuid4())
        aggregate = ConversationAggregate(conversation_id, user_id)

        start_event = ConversationEvent(
            conversation_id=conversation_id,
            user_id=user_id,
            type=EventType.CONVERSATION_STARTED,
            payload={"user_id": user_id},
            version=1,
        )
        aggregate.apply(start_event)

        # when
        message_event = ConversationEvent(
            conversation_id=conversation_id,
            user_id=user_id,
            type=EventType.NEW_MESSAGE,
            payload={
                "text": "Hello",
                "sender": "user@example.com",
                "message_id": str(uuid4()),
            },
            version=2,
        )
        aggregate.apply(message_event)

        # then
        assert aggregate.version == 2

    def test_cannot_add_message_to_inactive_conversation(self):
        # given
        conversation_id = str(uuid4())
        user_id = str(uuid4())
        aggregate = ConversationAggregate(conversation_id, user_id)

        # when/then - trying to add message without starting conversation
        message_event = ConversationEvent(
            conversation_id=conversation_id,
            user_id=user_id,
            type=EventType.NEW_MESSAGE,
            payload={
                "text": "Hello",
                "sender": "user@example.com",
                "message_id": str(uuid4()),
            },
            version=1,
        )

        with pytest.raises(
            ValueError, match="Cannot add message to conversation with status"
        ):
            aggregate.apply(message_event)

    def test_cannot_add_message_to_conversation_owned_by_another_user(self):
        # given
        conversation_id = str(uuid4())
        owner_user_id = str(uuid4())
        other_user_id = str(uuid4())
        aggregate = ConversationAggregate(conversation_id, owner_user_id)

        start_event = ConversationEvent(
            conversation_id=conversation_id,
            user_id=owner_user_id,
            type=EventType.CONVERSATION_STARTED,
            payload={"user_id": owner_user_id},
            version=1,
        )
        aggregate.apply(start_event)

        # when/then - other user trying to add message
        message_event = ConversationEvent(
            conversation_id=conversation_id,
            user_id=other_user_id,  # Different user
            type=EventType.NEW_MESSAGE,
            payload={
                "text": "Hello",
                "sender": "other@example.com",
                "message_id": str(uuid4()),
            },
            version=2,
        )

        with pytest.raises(
            ValueError, match=f"User {other_user_id} cannot add message to conversation"
        ):
            aggregate.apply(message_event)

    def test_delete_active_conversation(self):
        # given
        conversation_id = str(uuid4())
        user_id = str(uuid4())
        aggregate = ConversationAggregate(conversation_id, user_id)

        start_event = ConversationEvent(
            conversation_id=conversation_id,
            user_id=user_id,
            type=EventType.CONVERSATION_STARTED,
            payload={"user_id": user_id},
            version=1,
        )
        aggregate.apply(start_event)

        # when
        delete_event = ConversationEvent(
            conversation_id=conversation_id,
            user_id=user_id,
            type=EventType.CONVERSATION_DELETED,
            payload={"conversation_id": conversation_id},
            version=2,
        )
        aggregate.apply(delete_event)

        # then
        assert aggregate.status == ConversationStatus.INACTIVE
        assert aggregate.version == 2

    def test_cannot_delete_inactive_conversation(self):
        # given
        conversation_id = str(uuid4())
        user_id = str(uuid4())
        aggregate = ConversationAggregate(conversation_id, user_id)

        # when/then - trying to delete without starting conversation
        delete_event = ConversationEvent(
            conversation_id=conversation_id,
            user_id=user_id,
            type=EventType.CONVERSATION_DELETED,
            payload={"conversation_id": conversation_id},
            version=1,
        )

        with pytest.raises(ValueError, match="Cannot delete conversation with status"):
            aggregate.apply(delete_event)

    def test_cannot_delete_conversation_owned_by_another_user(self):
        # given
        conversation_id = str(uuid4())
        owner_user_id = str(uuid4())
        other_user_id = str(uuid4())
        aggregate = ConversationAggregate(conversation_id, owner_user_id)

        start_event = ConversationEvent(
            conversation_id=conversation_id,
            user_id=owner_user_id,
            type=EventType.CONVERSATION_STARTED,
            payload={"user_id": owner_user_id},
            version=1,
        )
        aggregate.apply(start_event)

        # when/then - other user trying to delete
        delete_event = ConversationEvent(
            conversation_id=conversation_id,
            user_id=other_user_id,  # Different user
            type=EventType.CONVERSATION_DELETED,
            payload={"conversation_id": conversation_id},
            version=2,
        )

        with pytest.raises(
            ValueError, match=f"User {other_user_id} cannot delete conversation"
        ):
            aggregate.apply(delete_event)

    def test_cannot_delete_wrong_conversation(self):
        # given
        conversation_id = str(uuid4())
        other_conversation_id = str(uuid4())
        user_id = str(uuid4())
        aggregate = ConversationAggregate(conversation_id, user_id)

        start_event = ConversationEvent(
            conversation_id=conversation_id,
            user_id=user_id,
            type=EventType.CONVERSATION_STARTED,
            payload={"user_id": user_id},
            version=1,
        )
        aggregate.apply(start_event)

        # when/then - trying to delete different conversation
        delete_event = ConversationEvent(
            conversation_id=other_conversation_id,  # Different conversation
            user_id=user_id,
            type=EventType.CONVERSATION_DELETED,
            payload={"conversation_id": other_conversation_id},
            version=2,
        )

        with pytest.raises(
            ValueError,
            match=f"Cannot delete conversation {conversation_id} because event conversation is {other_conversation_id}",
        ):
            aggregate.apply(delete_event)

    def test_apply_multiple_events(self):
        # given
        conversation_id = str(uuid4())
        user_id = str(uuid4())
        aggregate = ConversationAggregate(conversation_id, user_id)

        events = [
            ConversationEvent(
                conversation_id=conversation_id,
                user_id=user_id,
                type=EventType.CONVERSATION_STARTED,
                payload={"user_id": user_id},
                version=1,
            ),
            ConversationEvent(
                conversation_id=conversation_id,
                user_id=user_id,
                type=EventType.NEW_MESSAGE,
                payload={
                    "text": "Hello",
                    "sender": "user@example.com",
                    "message_id": str(uuid4()),
                },
                version=2,
            ),
            ConversationEvent(
                conversation_id=conversation_id,
                user_id=user_id,
                type=EventType.NEW_MESSAGE,
                payload={
                    "text": "How are you?",
                    "sender": "user@example.com",
                    "message_id": str(uuid4()),
                },
                version=3,
            ),
        ]

        # when
        aggregate.apply_events(events)

        # then
        assert aggregate.status == ConversationStatus.ACTIVE
        assert aggregate.version == 3

    def test_unknown_event_type_raises_error(self):
        # given
        conversation_id = str(uuid4())
        user_id = str(uuid4())
        aggregate = ConversationAggregate(conversation_id, user_id)

        # when/then
        event = ConversationEvent(
            conversation_id=conversation_id,
            user_id=user_id,
            type="UNKNOWN_EVENT",  # Invalid event type
            payload={},
            version=1,
        )

        with pytest.raises(ValueError, match="Unknown event type"):
            aggregate.apply(event)

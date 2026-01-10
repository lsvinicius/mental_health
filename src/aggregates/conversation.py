import datetime
from enum import Enum
from typing import List, Optional, Tuple

from src.db.models.event import ConversationEvent, EventType


class ConversationStatus(str, Enum):
    """Enum for conversation status."""

    ACTIVE = "active"
    INACTIVE = "inactive"


class ConversationAggregate:
    def __init__(self, conversation_id: str):
        self._conversation_id = conversation_id
        self._version = 0
        self._status: Optional[ConversationStatus] = None
        self._messages: List[Tuple[Optional[dict], datetime.datetime]] = []

    @property
    def status(self) -> Optional[ConversationStatus]:
        """Conversation status."""
        return self._status

    @property
    def conversation_id(self) -> str:
        """Conversation ID."""
        return self._conversation_id

    @property
    def version(self) -> int:
        """Conversation version."""
        return self._version

    def apply_events(self, events: List[ConversationEvent]):
        for event in events:
            self._apply(event)

    def _apply(self, event: ConversationEvent):
        if event.type == EventType.CONVERSATION_STARTED:
            self._handle_conversation_started()
        elif event.type == EventType.CONVERSATION_DELETED:
            self._handle_conversation_deleted()
        elif event.type == EventType.NEW_MESSAGE:
            self._handle_new_message(event)
        else:
            raise ValueError(f"Unknown event type: {event.type}")
        self._version += 1

    def _handle_conversation_started(self):
        if self._status is not None:
            raise ValueError(f"Cannot start conversation with status '{self._status}'")
        self._status = ConversationStatus.ACTIVE

    def _handle_new_message(self, event: ConversationEvent):
        if self._status != ConversationStatus.ACTIVE:
            raise ValueError(
                f"Cannot add message to conversation with status '{self._status}'"
            )
        self._messages.append((event.payload, event.timestamp))

    def _handle_conversation_deleted(self):
        if self._status != ConversationStatus.ACTIVE:
            raise ValueError(f"Cannot delete conversation with status '{self._status}'")
        self._status = ConversationStatus.INACTIVE

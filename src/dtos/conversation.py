from datetime import datetime
from typing import TypeVar, Optional, List
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict

T = TypeVar("T", bound="BaseTimeZoneDTO")


class BaseTimeZoneDTO(BaseModel):
    """Base DTO with recursive timezone conversion using zoneinfo."""

    def to_timezone(self: T, target_tz: ZoneInfo) -> T:
        """
        Returns a new instance of the DTO with all datetime fields
        converted to the target timezone.
        """
        data = self.model_dump()

        def convert_recursive(item):
            if isinstance(item, datetime):
                return item.astimezone(target_tz)

            elif isinstance(item, list):
                return [convert_recursive(i) for i in item]

            elif isinstance(item, dict):
                return {k: convert_recursive(v) for k, v in item.items()}

            return item

        converted_data = convert_recursive(data)
        return self.__class__(**converted_data)


class ConversationMessageDTO(BaseTimeZoneDTO):
    id: str
    text: str
    sender: str
    version: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationDTO(BaseTimeZoneDTO):
    id: str
    user_id: str
    status: Optional[str]
    messages: List[ConversationMessageDTO]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationRiskAnalysisDTO(BaseTimeZoneDTO):
    id: str
    conversation_id: str
    analysis: dict
    detected_risk: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

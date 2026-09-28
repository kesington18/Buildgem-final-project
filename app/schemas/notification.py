from pydantic import BaseModel, Field, ConfigDict
import uuid
from datetime import datetime


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    announcement_id: uuid.UUID
    is_read: bool
    created_at: datetime


class ReadNotification(BaseModel):
    is_read: bool


class NotificationPreferencesOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    group_id: uuid.UUID
    channel: str
    created_at: datetime


class NotificationPreferenceUpdate(BaseModel):
    group_ids: list[uuid.UUID]
    channel: str = Field(default="in_app")

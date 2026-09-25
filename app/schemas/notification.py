from pydantic import BaseModel, Field, ConfigDict
import uuid
from datetime import datetime
from typing import Optional


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
    group_id: Optional[uuid.UUID] = None
    keyword_id: Optional[uuid.UUID] = None
    category: Optional[str] = None
    channel: str
    created_at: datetime


class NotificationPreferenceUpdate(BaseModel):
    group_ids: Optional[list[uuid.UUID]] = None
    keyword_ids: Optional[list[uuid.UUID]] = None
    categories: Optional[list[str]] = None
    channel: str = Field(default="in_app")

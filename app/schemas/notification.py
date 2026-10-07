from pydantic import BaseModel, Field, ConfigDict
import uuid
from datetime import datetime
from typing import Optional

from app.schemas.announcement import AnnouncementOut


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    announcement_id: uuid.UUID
    is_read: bool
    created_at: datetime
    announcement: Optional[AnnouncementOut] = None  # so the feed can show the text without N extra calls


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

class PushKeys(BaseModel):
    p256dh: str
    auth: str


class PushSubscriptionCreate(BaseModel):
    endpoint: str
    keys: PushKeys

from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

from app.models.announcement import AnnouncementStatus


class KeywordBrief(BaseModel):
    id: UUID
    term: str
    category: str

    class Config:
        from_attributes = True


class AnnouncementUpdate(BaseModel):
    status: Optional[AnnouncementStatus] = None  # invalid values now return 422, not a DB 500
    message_content: Optional[str] = Field(default=None, min_length=1)


class AnnouncementOut(BaseModel):
    id: UUID
    message_content: str
    source_group_id: Optional[UUID]
    sender_info: Optional[str]
    message_timestamp: datetime
    status: str
    created_at: datetime
    keywords: list[KeywordBrief] = []

    class Config:
        from_attributes = True

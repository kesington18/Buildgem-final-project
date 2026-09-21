from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class AnnouncementUpdate(BaseModel):
    status: Optional[str] = None
    message_content: Optional[str] = None


class AnnouncementOut(BaseModel):
    id: UUID
    message_content: str
    source_group_id: Optional[UUID]
    sender_info: Optional[str]
    message_timestamp: datetime
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
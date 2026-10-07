from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class GroupCreate(BaseModel):
    chat_id: int
    name: str


class GroupUpdate(BaseModel):
    is_active: Optional[bool] = None
    name: Optional[str] = None


class GroupOut(BaseModel):
    """Admin view of a group, including who added/approved it."""
    id: UUID
    chat_id: int
    name: str
    is_active: bool
    owner_id: Optional[UUID] = None
    added_by: Optional[UUID] = None
    telegram_added_by_id: Optional[int] = None
    telegram_added_by_name: Optional[str] = None
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class GroupPublic(BaseModel):
    """Student view: no Telegram IDs or admin audit data."""
    id: UUID
    name: str

    class Config:
        from_attributes = True
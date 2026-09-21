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
    id: UUID
    chat_id: int
    name: str
    is_active: bool
    added_by: Optional[UUID]
    created_at: datetime

    class Config:
        from_attributes = True
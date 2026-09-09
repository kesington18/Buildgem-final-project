from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class KeywordCreate(BaseModel):
    term: str
    category: str
    is_active: bool = True


class KeywordUpdate(BaseModel):
    term: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None


class KeywordOut(BaseModel):
    id: UUID
    term: str
    category: str
    is_active: bool
    created_by: Optional[UUID]
    created_at: datetime

    class Config:
        from_attributes = True
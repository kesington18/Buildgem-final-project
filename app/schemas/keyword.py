from pydantic import BaseModel, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal

def _clean(value: Optional[str]) -> Optional[str]:
    return value.strip().lower() if value is not None else value


class KeywordCreate(BaseModel):
    term: str
    category: str
    is_active: bool = True

    @field_validator("term", "category")
    @classmethod
    def normalize(cls, value: str) -> str:
        return _clean(value)

class KeywordUpdate(BaseModel):
    term: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None
    status: Optional[Literal["approved", "pending"]] = None

    @field_validator("term", "category")
    @classmethod
    def normalize(cls, value: str) -> str:
        return _clean(value)

class KeywordOut(BaseModel):
    id: UUID
    term: str
    category: str
    is_active: bool
    group_id: Optional[UUID] = None
    status: str
    created_by: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True
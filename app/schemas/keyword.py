from pydantic import BaseModel, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional


class KeywordCreate(BaseModel):
    term: str
    category: str
    is_active: bool = True

    @field_validator("term")
    @classmethod
    def lowercase_term(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("category")
    @classmethod
    def lowercase_category(cls, value: str) -> str:
        return value.strip().lower()

class KeywordUpdate(BaseModel):
    term: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator("term")
    @classmethod
    def lowercase_term(cls, value: Optional[str]) -> Optional[str]:
        return value.strip().lower() if value is not None else value

    @field_validator("category")
    @classmethod
    def lowercase_category(cls, value: Optional[str]) -> Optional[str]:
        return value.strip().lower() if value is not None else value

class KeywordOut(BaseModel):
    id: UUID
    term: str
    category: str
    is_active: bool
    created_by: Optional[UUID]
    created_at: datetime

    class Config:
        from_attributes = True
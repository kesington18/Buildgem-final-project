from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.keyword import Keyword, KEYWORD_APPROVED

def get_active_keywords(db: Session, group_id: Optional[UUID] = None):
    """Keywords the bot should listen for in this group: enabled AND approved by its owner."""
    return db.query(Keyword).filter_by(is_active=True, status=KEYWORD_APPROVED, group_id=group_id).all()


def get_matched_keywords(text: str, keywords: list) -> list:
    text_lower = text.lower()
    return [kw for kw in keywords if kw.term.lower() in text_lower]


def contains_keyword(text: str, keywords: list[str]) -> bool:
    return any(keywording.lower() in text.lower() for keywording in keywords)
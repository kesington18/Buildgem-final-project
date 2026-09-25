from sqlalchemy.orm import Session
from app.models.keyword import Keyword

def get_active_keywords(db: Session):
    return db.query(Keyword).filter_by(is_active=True).all()

def get_matched_keywords(text: str, keywords: list) -> list:
    text_lower = text.lower()
    return [kw for kw in keywords if kw.term.lower() in text_lower]


def contains_keyword(text: str, keywords: list[str]) -> bool:
    return any(keywording.lower() in text.lower() for keywording in keywords)
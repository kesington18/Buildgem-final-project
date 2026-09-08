from sqlalchemy.orm import Session
from app.models.keyword import Keyword

def get_active_keywords(db: Session):
    rows = db.query(Keyword).filter_by(is_active=True).all()
    return [row.term for row in rows]

def contains_keyword(text: str, keywords: list[str]) -> bool:
    return any(keywording.lower() in text.lower() for keywording in keywords)
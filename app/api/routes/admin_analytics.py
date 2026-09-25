from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_admin
from app.models.announcement import Announcement, announcement_keywords
from app.models.keyword import Keyword
from app.models.group import TelegramGroup

router = APIRouter(prefix="/admin", tags=["admin-analytics"])


@router.get("/analytics")
def analytics(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    per_category = (
        db.query(Keyword.category, func.count(func.distinct(Announcement.id)))
        .join(announcement_keywords, announcement_keywords.c.keyword_id == Keyword.id)
        .join(Announcement, Announcement.id == announcement_keywords.c.announcement_id)
        .group_by(Keyword.category)
        .all()
    )
    per_group = (
        db.query(TelegramGroup.name, func.count(Announcement.id))
        .join(Announcement, Announcement.source_group_id == TelegramGroup.id)
        .group_by(TelegramGroup.name)
        .all()
    )
    return {
        "per_category": dict(per_category),
        "per_group": dict(per_group),
    }
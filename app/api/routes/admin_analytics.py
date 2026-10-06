from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_manager, managed_group_ids
from app.db.session import get_db
from app.models.announcement import Announcement, AnnouncementStatus, announcement_keywords
from app.models.group import TelegramGroup
from app.models.keyword import Keyword

router = APIRouter(prefix="/admin", tags=["admin-analytics"])


@router.get("/analytics")
def analytics(db: Session = Depends(get_db), user=Depends(get_manager)):
    """Site admins see everything; group owners see numbers for their own groups only."""
    scope = managed_group_ids(user, db)  # None = all groups

    def in_scope_announcements(q):
        return q if scope is None else q.filter(Announcement.source_group_id.in_(scope))

    per_category = in_scope_announcements(
        db.query(Keyword.category, func.count(func.distinct(Announcement.id)))
        .join(announcement_keywords, announcement_keywords.c.keyword_id == Keyword.id)
        .join(Announcement, Announcement.id == announcement_keywords.c.announcement_id)
    ).group_by(Keyword.category).all()

    per_group = in_scope_announcements(
        db.query(TelegramGroup.name, func.count(Announcement.id))
        .join(Announcement, Announcement.source_group_id == TelegramGroup.id)
    ).group_by(TelegramGroup.name).all()

    since = datetime.now(timezone.utc) - timedelta(days=30)
    day = func.date(Announcement.message_timestamp)
    over_time = in_scope_announcements(
        db.query(day, func.count(Announcement.id)).filter(Announcement.message_timestamp >= since)
    ).group_by(day).order_by(day).all()

    groups_q = db.query(func.count(TelegramGroup.id))
    keywords_q = db.query(func.count(Keyword.id)).filter(Keyword.status == "approved")
    if scope is not None:
        groups_q = groups_q.filter(TelegramGroup.id.in_(scope))
        keywords_q = keywords_q.filter(Keyword.group_id.in_(scope))

    totals = {
        "announcements": in_scope_announcements(db.query(func.count(Announcement.id))).scalar() or 0,
        "active_announcements": in_scope_announcements(
            db.query(func.count(Announcement.id)).filter(Announcement.status == AnnouncementStatus.active)
        ).scalar() or 0,
        "keywords": keywords_q.scalar() or 0,
        "groups": groups_q.filter(TelegramGroup.is_active.is_(True)).scalar() or 0,
        "pending_groups": groups_q.filter(TelegramGroup.is_active.is_(False)).scalar() or 0,
    }

    return {
        "per_category": dict(per_category),
        "per_group": dict(per_group),
        "over_time": {str(d): n for d, n in over_time},
        "totals": totals,
    }

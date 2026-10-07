import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.announcement import Announcement, AnnouncementStatus
from app.models.keyword import Keyword
from app.models.user import User
from app.schemas.announcement import AnnouncementOut

router = APIRouter(prefix="/api/v1/announcements", tags=["Announcements"])


@router.get("", response_model=list[AnnouncementOut])
def get_announcements(
    response: Response,
    q: Optional[str] = None,
    group_id: Optional[uuid.UUID] = None,
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Students only ever see active announcements (archived/deleted are admin-only).
    query = (
        db.query(Announcement)
        .options(selectinload(Announcement.keywords))
        .filter(Announcement.status == AnnouncementStatus.active)
    )
    if q:
        query = query.filter(Announcement.message_content.ilike(f"%{q}%"))
    if group_id is not None:
        query = query.filter(Announcement.source_group_id == group_id)
    if date_from is not None:
        query = query.filter(Announcement.message_timestamp >= date_from)
    if date_to is not None:
        query = query.filter(Announcement.message_timestamp <= date_to)
    if category:
        query = query.filter(Announcement.keywords.any(Keyword.category == category.strip().lower()))
    if keyword:
        query = query.filter(Announcement.keywords.any(Keyword.term.ilike(f"%{keyword.strip()}%")))

    response.headers["X-Total-Count"] = str(query.count())

    # Newest first, with a tiebreaker so pagination is stable.
    return (
        query.order_by(Announcement.message_timestamp.desc(), Announcement.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )


@router.get("/filters")
def get_filter_options(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Categories and keywords for the feed's filter dropdowns."""
    rows = db.query(Keyword).filter(Keyword.is_active.is_(True)).order_by(Keyword.term).all()
    return {
        "categories": sorted({k.category for k in rows}),
        "keywords": [k.term for k in rows],
    }


@router.get("/{announcement_id}", response_model=AnnouncementOut)
def get_announcement_by_id(
    announcement_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not announcement or announcement.status != AnnouncementStatus.active:
        raise HTTPException(status_code=404, detail=f"Announcement with id {announcement_id} does not exist")
    return announcement

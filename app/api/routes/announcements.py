import uuid
from typing import Optional
from fastapi import Query, Depends, APIRouter, HTTPException
from app.db.session import get_db
from app.api.deps import get_current_user
from datetime import datetime
from app.models.announcement import Announcement, announcement_keywords
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.keyword import Keyword
from app.schemas.announcement import AnnouncementOut

router = APIRouter(prefix="/announcements", tags=["Announcements"])

@router.get("", response_model=list[AnnouncementOut])
def get_announcements(
        q: Optional[str] = None,
        group_id: Optional[uuid.UUID] = None,
        category: Optional[str] = None,
        keyword: Optional[str] = None,
        date_from: Optional[datetime]= None,
        date_to: Optional[datetime] = None,
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=10, ge=1, le=100),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    announcement_query = db.query(Announcement)
    if q is not None:
        announcement_query = announcement_query.filter(Announcement.message_content.ilike(f"%{q}%"))
    if group_id is not None:
        announcement_query = announcement_query.filter(Announcement.source_group_id == group_id)
    if date_from is not None:
        announcement_query = announcement_query.filter(Announcement.message_timestamp >= date_from)
    if date_to is not None:
        announcement_query = announcement_query.filter(Announcement.message_timestamp <= date_to)

    announcement_query = announcement_query.join(
        announcement_keywords,
        Announcement.id == announcement_keywords.c.announcement.id
    )
    announcement_query = announcement_query.join(
        Keyword,
        announcement_keywords.c.keyword.id == Keyword.id
    )

    if category is not None:
        announcement_query = announcement_query.filter(Keyword.category == category)

    if keyword is not None:
        announcement_query = announcement_query.filter(Keyword.term.ilike(f"%{keyword}%"))

    announcement_query = announcement_query.distinct()

    offset = (page - 1) * page_size
    announcement_query = announcement_query.offset(offset).limit(page_size)

    return announcement_query.all()


@router.get("/{announcement_id}", response_model=AnnouncementOut)
def get_announcement_by_id(
        announcement_id: uuid.UUID,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()

    if not announcement or announcement.status != "active":
        raise HTTPException(status_code=404, detail=f"Announcement with id {announcement_id} does not exist")

    return announcement
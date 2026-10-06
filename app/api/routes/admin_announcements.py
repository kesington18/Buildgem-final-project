from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_manager, managed_group_ids
from app.db.session import get_db
from app.models.announcement import Announcement, AnnouncementStatus
from app.models.notifications import Notification
from app.schemas.announcement import AnnouncementUpdate, AnnouncementOut

router = APIRouter(prefix="/admin/announcements", tags=["admin-announcements"])


def _get_managed_announcement(db: Session, user, announcement_id: UUID) -> Announcement:
    ann = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    scope = managed_group_ids(user, db)
    if not ann or (scope is not None and ann.source_group_id not in scope):
        raise HTTPException(status_code=404, detail="Announcement not found")
    return ann


@router.get("", response_model=list[AnnouncementOut])
def list_announcements(
    response: Response,
    status: Optional[AnnouncementStatus] = None,
    group_id: Optional[UUID] = None,
    q: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    user=Depends(get_manager),
):
    """Moderation queue: every announcement (active and archived), newest first."""
    query = db.query(Announcement).options(selectinload(Announcement.keywords))
    scope = managed_group_ids(user, db)  # None = site admin (everything)
    if scope is not None:
        query = query.filter(Announcement.source_group_id.in_(scope))
    if status is not None:
        query = query.filter(Announcement.status == status)
    else:
        query = query.filter(Announcement.status != AnnouncementStatus.deleted)
    if group_id is not None:
        query = query.filter(Announcement.source_group_id == group_id)
    if q:
        query = query.filter(Announcement.message_content.ilike(f"%{q}%"))

    response.headers["X-Total-Count"] = str(query.count())
    return (
        query.order_by(Announcement.message_timestamp.desc(), Announcement.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )


@router.patch("/{announcement_id}", response_model=AnnouncementOut)
def update_announcement(announcement_id: UUID, payload: AnnouncementUpdate, db: Session = Depends(get_db), user=Depends(get_manager)):
    ann = _get_managed_announcement(db, user, announcement_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(ann, field, value)
    db.commit()
    db.refresh(ann)
    return ann


@router.delete("/{announcement_id}")
def delete_announcement(announcement_id: UUID, db: Session = Depends(get_db), user=Depends(get_manager)):
    ann = _get_managed_announcement(db, user, announcement_id)
    # notifications.announcement_id is a foreign key; remove dependants first or Postgres rejects the delete
    db.query(Notification).filter(Notification.announcement_id == ann.id).delete(synchronize_session=False)
    db.delete(ann)  # also clears announcement_keywords rows via the relationship
    db.commit()
    return {"detail": "Deleted"}

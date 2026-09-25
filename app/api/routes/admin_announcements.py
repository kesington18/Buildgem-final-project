from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.api.deps import get_current_admin
from app.models.announcement import Announcement, announcement_keywords
from app.models.keyword import Keyword
from app.models.group import TelegramGroup
from app.schemas.announcement import AnnouncementUpdate, AnnouncementOut

router = APIRouter(prefix="/admin/announcements", tags=["admin-announcements"])


@router.patch("/{announcement_id}", response_model=AnnouncementOut)
def update_announcement(announcement_id: UUID, payload: AnnouncementUpdate, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    ann = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(ann, field, value)
    db.commit()
    db.refresh(ann)
    return ann


@router.delete("/{announcement_id}")
def delete_announcement(announcement_id: UUID, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    ann = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")
    db.delete(ann)
    db.commit()
    return {"detail": "Deleted"}

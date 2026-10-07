from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_manager, managed_group_ids
from app.db.session import get_db
from app.models.announcement import Announcement
from app.models.group import TelegramGroup
from app.models.keyword import Keyword
from app.models.notification_preferences import NotificationPreferences
from app.schemas.group import GroupCreate, GroupUpdate, GroupOut

router = APIRouter(prefix="/admin/groups", tags=["admin-groups"])
# Site admins see/manage every group. A group owner sees/manages only the groups they claimed.


def _get_managed_group(db: Session, user, group_id: UUID) -> TelegramGroup:
    group = db.query(TelegramGroup).filter(TelegramGroup.id == group_id).first()
    scope = managed_group_ids(user, db)
    if not group or (scope is not None and group.id not in scope):
        raise HTTPException(status_code=404, detail="Group not found")
    return group


@router.get("", response_model=list[GroupOut])
def list_groups(db: Session = Depends(get_db), user=Depends(get_manager)):
    query = db.query(TelegramGroup)
    scope = managed_group_ids(user, db)
    if scope is not None:
        query = query.filter(TelegramGroup.id.in_(scope))
    return query.order_by(TelegramGroup.created_at.desc()).all()


@router.post("", response_model=GroupOut)
def create_group(payload: GroupCreate, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    """Site admin only: manually register a group by chat ID (created inactive)."""
    if db.query(TelegramGroup).filter(TelegramGroup.chat_id == payload.chat_id).first():
        raise HTTPException(status_code=409, detail="A group with this chat ID already exists")
    group = TelegramGroup(chat_id=payload.chat_id, name=payload.name, is_active=False)
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


@router.patch("/{group_id}", response_model=GroupOut)
def authorize_group(group_id: UUID, payload: GroupUpdate, db: Session = Depends(get_db), user=Depends(get_manager)):
    group = _get_managed_group(db, user, group_id)

    changes = payload.model_dump(exclude_unset=True)
    was_active = group.is_active
    for field, value in changes.items():
        setattr(group, field, value)

    if changes.get("is_active") is True and not was_active:
        group.approved_by = user.id
        group.approved_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(group)
    return group


@router.delete("/{group_id}")
def revoke_group(group_id: UUID, db: Session = Depends(get_db), user=Depends(get_manager)):
    group = _get_managed_group(db, user, group_id)

    has_announcements = db.query(Announcement.id).filter(Announcement.source_group_id == group.id).first()
    if has_announcements:
        # Keep history intact (announcements reference the group); just stop monitoring it.
        group.is_active = False
        db.commit()
        return {"detail": "Group deactivated (kept because it has announcements)"}

    db.query(NotificationPreferences).filter(NotificationPreferences.group_id == group.id).delete()
    db.query(Keyword).filter(Keyword.group_id == group.id).delete()
    db.delete(group)
    db.commit()
    return {"detail": "Deleted"}

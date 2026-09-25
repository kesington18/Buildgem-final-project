from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.api.deps import get_current_admin
from app.models.group import TelegramGroup
from app.schemas.group import GroupCreate, GroupUpdate, GroupOut

router = APIRouter(prefix="/admin/groups", tags=["admin-groups"])


@router.get("", response_model=list[GroupOut])
def list_groups(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    return db.query(TelegramGroup).all()


@router.post("", response_model=GroupOut)
def create_group(payload: GroupCreate, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    group = TelegramGroup(chat_id=payload.chat_id, name=payload.name, added_by=admin.id)
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


@router.patch("/{group_id}", response_model=GroupOut)
def authorize_group(group_id: UUID, payload: GroupUpdate, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    group = db.query(TelegramGroup).filter(TelegramGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(group, field, value)
    db.commit()
    db.refresh(group)
    return group


@router.delete("/{group_id}")
def revoke_group(group_id: UUID, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    group = db.query(TelegramGroup).filter(TelegramGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    db.delete(group)
    db.commit()
    return {"detail": "Deleted"}
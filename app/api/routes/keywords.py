from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from uuid import UUID
from typing import Optional

from app.db.session import get_db
from app.api.deps import get_current_user, can_manage_group
from app.models.group import TelegramGroup
from app.models.keyword import Keyword, KEYWORD_PENDING, KEYWORD_APPROVED
from app.models.user import User
from app.schemas.keyword import KeywordCreate, KeywordUpdate, KeywordOut

router = APIRouter(prefix="/api/v1/groups/{group_id}/keywords", tags=["group-keywords"])

# stops one student flooding a group's suggestion queue
MAX_PENDING_PER_STUDENT = 10

def _get_group(db: Session, group_id: UUID) -> TelegramGroup:
    group = db.query(TelegramGroup).filter(TelegramGroup.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=404,
            detail="Group not found",
        )
    return group

def _get_keyword(db: Session, group: TelegramGroup, keyword_id: UUID) -> Keyword:
    kw = db.query(Keyword).filter(Keyword.id == keyword_id, Keyword.group_id == group.id).first()
    if not kw:
        raise HTTPException(
            status_code=404,
            detail="Keyword not found",
        )
    return kw


"""Owner/admin: every keyword (filter with ?status=pending for the review queue).
    Other students: approved keywords plus their own pending suggestions."""
@router.get("", response_model=list[KeywordOut])
def list_keywords(
        group_id: UUID,
        status: Optional[str] = None,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user),
):
    group = _get_group(db, group_id)
    manager = can_manage_group(user, group)
    if not manager and not group.is_active:
        raise HTTPException(status_code=404, detail="Group not found")

    query = db.query(Keyword).filter(Keyword.group_id == group.id)
    if manager:
        if status:
            query = query.filter(Keyword.status == status)
    else:
        query = query.filter(or_(
            Keyword.status == KEYWORD_APPROVED,
            and_(Keyword.status == KEYWORD_PENDING, Keyword.created_by == user.id),
        ))
    return query.order_by(Keyword.term).all()


"""Owner/admin: added immediately. Any other student: saved as a pending suggestion."""
@router.post("", response_model=KeywordOut)
def create_keyword(
    group_id: UUID,
    payload: KeywordCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Owner/admin: added immediately. Any other student: saved as a pending suggestion."""
    group = _get_group(db, group_id)
    manager = can_manage_group(user, group)
    if not manager and not group.is_active:
        raise HTTPException(status_code=404, detail="Group not found")
    if not payload.term or not payload.category:
        raise HTTPException(status_code=422, detail="term and category must not be empty")
    if db.query(Keyword).filter(Keyword.group_id == group.id, Keyword.term == payload.term).first():
        raise HTTPException(status_code=409, detail="Keyword already exists for this group")

    if manager:
        status = KEYWORD_APPROVED
    else:
        pending = db.query(Keyword).filter(
            Keyword.group_id == group.id, Keyword.created_by == user.id, Keyword.status == KEYWORD_PENDING
        ).count()
        if pending >= MAX_PENDING_PER_STUDENT:
            raise HTTPException(status_code=429, detail="Too many pending suggestions; wait for the group owner to review them")
        status = KEYWORD_PENDING

    kw = Keyword(
        term=payload.term, category=payload.category, is_active=payload.is_active,
        group_id=group.id, status=status, created_by=user.id,
    )
    db.add(kw)
    db.commit()
    db.refresh(kw)
    return kw


"""Owner/admin only: rename, recategorise, enable/disable, or approve a suggestion."""
@router.patch("/{keyword_id}", response_model=KeywordOut)
def update_keyword(
    group_id: UUID,
    keyword_id: UUID,
    payload: KeywordUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):

    group = _get_group(db, group_id)
    if not can_manage_group(user, group):
        raise HTTPException(status_code=403, detail="Only the group owner can edit keywords")
    kw = _get_keyword(db, group, keyword_id)

    changes = payload.model_dump(exclude_unset=True)
    new_term = changes.get("term")
    if new_term is not None:
        if not new_term:
            raise HTTPException(status_code=422, detail="term must not be empty")
        clash = db.query(Keyword).filter(
            Keyword.group_id == group.id, Keyword.term == new_term, Keyword.id != kw.id
        ).first()
        if clash:
            raise HTTPException(status_code=409, detail="Keyword already exists for this group")
    for field, value in changes.items():
        if value is None and field in ("term", "category", "status"):
            continue
        setattr(kw, field, value)
    db.commit()
    db.refresh(kw)
    return kw

"""Owner/admin can delete any keyword (this also rejects a suggestion).
    A student can withdraw their own pending suggestion."""
@router.delete("/{keyword_id}")
def delete_keyword(
    group_id: UUID,
    keyword_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):

    group = _get_group(db, group_id)
    kw = _get_keyword(db, group, keyword_id)
    own_pending = kw.status == KEYWORD_PENDING and kw.created_by == user.id
    if not (can_manage_group(user, group) or own_pending):
        raise HTTPException(status_code=403, detail="Only the group owner can delete keywords")
    db.delete(kw)
    db.commit()
    return {"detail": "Deleted"}
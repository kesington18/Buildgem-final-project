from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.api.deps import get_current_admin
from app.models.keyword import Keyword
from app.schemas.keyword import KeywordCreate, KeywordUpdate, KeywordOut

router = APIRouter(prefix="/admin/keywords", tags=["admin-keywords"])


@router.get("", response_model=list[KeywordOut])
def list_keywords(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    return db.query(Keyword).all()


@router.post("", response_model=KeywordOut)
def create_keyword(payload: KeywordCreate, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    kw = Keyword(**payload.model_dump(), created_by=admin.id)
    db.add(kw)
    db.commit()
    db.refresh(kw)
    return kw


@router.patch("/{keyword_id}", response_model=KeywordOut)
def update_keyword(keyword_id: UUID, payload: KeywordUpdate, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    kw = db.query(Keyword).filter(Keyword.id == keyword_id).first()
    if not kw:
        raise HTTPException(status_code=404, detail="Keyword not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(kw, field, value)
    db.commit()
    db.refresh(kw)
    return kw


@router.delete("/{keyword_id}")
def delete_keyword(keyword_id: UUID, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    kw = db.query(Keyword).filter(Keyword.id == keyword_id).first()
    if not kw:
        raise HTTPException(status_code=404, detail="Keyword not found")
    db.delete(kw)
    db.commit()
    return {"detail": "Deleted"}
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_admin
from app.models.admin_allowlist import AdminAllowlistEntry
from app.models.user import User
from app.schemas.otp import AdminAllowlistCreate

router = APIRouter(prefix="/admin/allowlist", tags=["admin-allowlist"])


@router.post("")
def add_to_allowlist(payload: AdminAllowlistCreate, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="A user with this email already exists")

    if db.query(AdminAllowlistEntry).filter(AdminAllowlistEntry.email == payload.email, AdminAllowlistEntry.is_used == False).first():
        raise HTTPException(status_code=400, detail="Email already pre-approved and pending")

    entry = AdminAllowlistEntry(email=payload.email, added_by=admin.id)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return {"detail": f"{payload.email} added to admin allowlist"}


@router.get("")
def list_allowlist(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    return db.query(AdminAllowlistEntry).all()
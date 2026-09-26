from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.group import TelegramGroup
from app.db.session import get_db
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/v1/groups", tags=["Groups"])

@router.get("")
def get_groups(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    return db.query(TelegramGroup).filter(TelegramGroup.is_active.is_(True)).all()
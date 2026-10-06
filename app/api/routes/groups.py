from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.group import TelegramGroup
from app.models.group_claim import GroupClaimCode
from app.models.user import User
from app.schemas.group import GroupOut, GroupPublic
from app.services.group_claim import CODE_TTL, new_claim_code

router = APIRouter(prefix="/api/v1/groups", tags=["Groups"])


@router.get("", response_model=list[GroupPublic])
def get_groups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Approved groups students can filter by / subscribe to (id and name only)."""
    return (
        db.query(TelegramGroup)
        .filter(TelegramGroup.is_active.is_(True))
        .order_by(TelegramGroup.name)
        .all()
    )


@router.get("/mine", response_model=list[GroupOut])
def my_groups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Groups this student has claimed (empty for everyone else)."""
    return db.query(TelegramGroup).filter(TelegramGroup.owner_id == current_user.id).order_by(TelegramGroup.name).all()


@router.post("/claim-code")
def create_claim_code(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Step 1 of becoming a group owner. The student then sends `/claim CODE` in their
    Telegram group (where the bot has already been added) within 15 minutes."""
    db.query(GroupClaimCode).filter(
        GroupClaimCode.user_id == current_user.id, GroupClaimCode.used_at.is_(None)
    ).delete()  # only one live code per student
    code = new_claim_code()
    expires_at = datetime.now(timezone.utc) + CODE_TTL
    db.add(GroupClaimCode(user_id=current_user.id, code=code, expires_at=expires_at))
    db.commit()
    return {"code": code, "expires_at": expires_at, "command": f"/claim {code}"}

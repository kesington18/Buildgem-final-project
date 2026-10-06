import uuid
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError

from app.core.security import decode_token
from app.db.session import get_db
from app.models.group import TelegramGroup
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise credentials_exception
        user_id = uuid.UUID(str(payload.get("sub")))
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_admin(user: User = Depends(get_current_user)) -> User:
    if user.role.value != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user

# group ownership
# Site admins (role=admin) can manage every group. A student who has claimed a
# group (TelegramGroup.owner_id == their id) can manage that group only.

def is_site_admin(user: User) -> bool:
    return user.role.value == "admin"

def managed_group_ids(user: User, db: Session) -> Optional[list]:
    """None means 'all groups' (site admin); otherwise the IDs of groups this user owns."""
    if is_site_admin(user):
        return None
    return [row.id for row in db.query(TelegramGroup.id).filter(TelegramGroup.owner_id == user.id).all()]

def get_manager(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
    """Allows site admins and anyone who owns at least one group."""
    ids = managed_group_ids(user, db)
    if ids is not None and not ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Group owner access required",
        )
    return user

def can_manage_group(user: User, group: TelegramGroup) -> bool:
    return is_site_admin(user) or group.owner_id == user.id
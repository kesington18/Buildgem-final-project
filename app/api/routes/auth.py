from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.group import TelegramGroup
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserOut, MeOut, Token, RefreshRequest
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _authenticate(db: Session, email: str, password: str) -> Token:
    user = db.query(User).filter(User.email == email.strip().lower()).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return Token(
        access_token=create_access_token(str(user.id), user.role.value),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """JSON login, used by the frontend."""
    return _authenticate(db, payload.email, payload.password)


@router.post("/token", response_model=Token, include_in_schema=True)
def login_form(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Form login, used by Swagger's Authorize button. Put the email in the 'username' field."""
    return _authenticate(db, form.username, form.password)


@router.post("/refresh", response_model=Token)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    try:
        decoded = decode_token(payload.refresh_token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    if decoded.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user = db.query(User).filter(User.id == decoded["sub"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return Token(
        access_token=create_access_token(str(user.id), user.role.value),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.get("/me", response_model=MeOut)
def me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Used by the frontend after login to learn the user's name, role and whether they own a group."""
    owns_group = db.query(TelegramGroup.id).filter(TelegramGroup.owner_id == current_user.id).first() is not None
    out = MeOut.model_validate(current_user)
    out.is_group_owner = owns_group
    return out


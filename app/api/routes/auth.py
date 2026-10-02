from datetime import datetime, timezone
from app.models.otp import OtpCode, OtpPurpose, generate_otp_code
from app.models.admin_allowlist import AdminAllowlistEntry
from app.models.user import UserRole
from app.schemas.otp import RequestAdminOtp, VerifyAdminOtp
from app.services.email_sender import send_otp_email
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import JWTError

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserOut, Token, RefreshRequest
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


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return Token(
        access_token=create_access_token(str(user.id), user.role.value),
        refresh_token=create_refresh_token(str(user.id)),
    )

@router.post("/admin/request-otp")
def request_admin_otp(payload: RequestAdminOtp, db: Session = Depends(get_db)):
    allowlist_entry = (
        db.query(AdminAllowlistEntry)
        .filter(AdminAllowlistEntry.email == payload.email, AdminAllowlistEntry.is_used == False)
        .first()
    )
    if not allowlist_entry:
        raise HTTPException(status_code=403, detail="This email is not approved for admin signup")

    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="An account with this email already exists")

    otp_code = OtpCode(email=payload.email, code=generate_otp_code(), purpose=OtpPurpose.admin_signup)
    db.add(otp_code)
    db.commit()

    send_otp_email(payload.email, otp_code.code)

    return {"detail": "OTP sent to email"}


@router.post("/admin/verify-otp", response_model=UserOut)
def verify_admin_otp(payload: VerifyAdminOtp, db: Session = Depends(get_db)):
    otp_record = (
        db.query(OtpCode)
        .filter(
            OtpCode.email == payload.email,
            OtpCode.code == payload.otp,
            OtpCode.purpose == OtpPurpose.admin_signup,
            OtpCode.is_used == False,
        )
        .order_by(OtpCode.created_at.desc())
        .first()
    )

    if not otp_record:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    if otp_record.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="OTP has expired")

    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="An account with this email already exists")

    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=UserRole.admin,
    )
    db.add(user)

    otp_record.is_used = True

    allowlist_entry = db.query(AdminAllowlistEntry).filter(AdminAllowlistEntry.email == payload.email).first()
    if allowlist_entry:
        allowlist_entry.is_used = True

    db.commit()
    db.refresh(user)
    return user


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
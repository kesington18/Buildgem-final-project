import uuid
import enum
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import Column, String, Boolean, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.session import Base


class OtpPurpose(str, enum.Enum):
    admin_signup = "admin_signup"


def generate_otp_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"  # 6-digit, zero-padded


def default_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=10)


class OtpCode(Base):
    __tablename__ = "otp_codes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, nullable=False, index=True)
    code = Column(String(6), nullable=False)
    purpose = Column(Enum(OtpPurpose), nullable=False, default=OtpPurpose.admin_signup)
    is_used = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False, default=default_expiry)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
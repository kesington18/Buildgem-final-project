from datetime import datetime, timezone
from typing import Optional

from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.models.revoked_token import RevokedToken


def is_revoked(db: Session, jti: Optional[str]) -> bool:
    # Tokens issued before revocation existed have no jti; they simply expire on schedule.
    return bool(jti) and db.get(RevokedToken, jti) is not None


def revoke_token(db: Session, token: Optional[str], expected_type: str) -> bool:
    """Revoke one token if it is valid, of the expected type, and has a jti. Never raises on bad input."""
    if not token:
        return False
    try:
        payload = decode_token(token)
    except JWTError:  # already expired or malformed: nothing left to revoke
        return False
    jti = payload.get("jti")
    if payload.get("type") != expected_type or not jti:
        return False
    expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    db.merge(RevokedToken(jti=jti, expires_at=expires_at))
    return True


def purge_expired(db: Session) -> None:
    db.query(RevokedToken).filter(RevokedToken.expires_at < datetime.now(timezone.utc)).delete()

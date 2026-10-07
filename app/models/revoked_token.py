from sqlalchemy import Column, String, DateTime

from app.db.session import Base


class RevokedToken(Base):
    """Tokens invalidated by logout. A row can be deleted once expires_at has passed,
    because the token would be rejected as expired anyway."""
    __tablename__ = "revoked_tokens"

    jti = Column(String, primary_key=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)

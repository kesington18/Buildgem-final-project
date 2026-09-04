import uuid

from sqlalchemy import Column, String, Boolean, DateTime, BigInteger, ForeignKey, false
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.session import Base


class TelegramGroup(Base):
    __tablename__ = "telegram_groups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = Column(BigInteger, unique=True, nullable=False)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=False, server_default=false(), nullable=False)
    added_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
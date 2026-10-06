import uuid

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.session import Base

KEYWORD_APPROVED = "approved"
KEYWORD_PENDING = "pending"


class Keyword(Base):
    """A keyword the bot listens for in ONE group. Each group's owner controls its list."""
    __tablename__ = "keywords"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    term = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    group_id = Column(UUID(as_uuid=True), ForeignKey("telegram_groups.id"), nullable=True, index=True)
    status = Column(String, nullable=False, default=KEYWORD_APPROVED, server_default=KEYWORD_APPROVED)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint('group_id', 'term', name="uq_keyword_group_term"),)
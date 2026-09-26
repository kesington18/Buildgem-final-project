from app.db.session import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy import Column, UniqueConstraint, ForeignKey, Boolean, DateTime, true
from datetime import datetime


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    announcement_id = Column(UUID(as_uuid=True), ForeignKey("announcements.id"))
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)

    __table_args__ = (
        UniqueConstraint("user_id", "announcement_id", name="unique_user_announcement"),
    )

from app.db.session import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy import Column, UniqueConstraint, ForeignKey, Boolean, DateTime, true
from datetime import datetime
from sqlalchemy.orm import relationship


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    announcement_id = Column(UUID(as_uuid=True), ForeignKey("announcements.id"))
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)

    # user = relationship("User", back_populates="notifications")
    # announcement = relationship("Announcement")

    __table_args__ = (
        UniqueConstraint("user_id", "announcement_id", name="unique_user_announcement"),
    )

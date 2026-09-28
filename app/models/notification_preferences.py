from app.db.session import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, UniqueConstraint, ForeignKey, Boolean, DateTime
from datetime import datetime


class NotificationPreferences(Base):
    __tablename__ = "notification_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    group_id = Column(UUID(as_uuid=True), ForeignKey("telegram_groups.id"), nullable=False)
    channel = Column(String, default="in_app")
    created_at = Column(DateTime, default=datetime.now)

    __table_args__ = (
        UniqueConstraint("user_id", "group_id", name="unique_user_group_subscription"),
    )
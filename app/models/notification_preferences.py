from app.db.session import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, CheckConstraint, ForeignKey, Boolean, DateTime
from datetime import datetime


class NotificationPreferences(Base):
    __tablename__ = "notification_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    group_id = Column(UUID(as_uuid=True), ForeignKey("telegram_groups.id"), nullable=True)
    keyword_id = Column(UUID(as_uuid=True), ForeignKey("keywords.id"), nullable=True)
    category = Column(String, nullable=True)
    channel = Column(String, default="in_app")
    created_at = Column(DateTime, default=datetime.now)

    __table_args__ = (
        CheckConstraint(
            "NOT (group_id IS NULL AND keyword_id IS NULL AND category IS NULL)",
            name="check_at_least_one_not_null"
        ),
    )
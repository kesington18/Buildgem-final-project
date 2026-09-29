from app.db.session import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, DateTime, ForeignKey
from datetime import datetime

class PushSubscription(Base):
    __tablename__ = "push_subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    endpoint = Column(String, nullable=False, unique=True)
    p256dh_key = Column(String, nullable=False)
    auth_key = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
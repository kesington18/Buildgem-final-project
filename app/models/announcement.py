import uuid
import enum

from sqlalchemy import Column, Text, String, DateTime, ForeignKey, Enum, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class AnnouncementStatus(str, enum.Enum):
    active = "active"
    archived = "archived"
    deleted = "deleted"

# Many-to-many join table between announcements and keywords
announcement_keywords = Table(
    "announcement_keywords",
    Base.metadata,
    Column("announcement_id", UUID(as_uuid=True), ForeignKey("announcements.id"), primary_key=True),
    Column("keyword_id", UUID(as_uuid=True), ForeignKey("keywords.id"), primary_key=True),
)

class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_content = Column(Text, nullable=False)
    source_group_id = Column(UUID(as_uuid=True), ForeignKey("telegram_groups.id"))
    sender_info = Column(String, nullable=False)
    message_timestamp = Column(DateTime(timezone=True), nullable=False)
    status = Column(Enum(AnnouncementStatus), default=AnnouncementStatus.active)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    keywords = relationship("Keyword", secondary=announcement_keywords, backref="announcements")
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.announcement import Announcement

def save_announcement(db: Session, message: dict, group):
    announcement = Announcement(
        message_content=message["text"],
        source_group_id=group.id,
        sender_info=message.get("from", {}).get("username"),
        message_timestamp=datetime.fromtimestamp(message["date"]),
    )
    db.add(announcement)
    db.commit()
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.celery_app import celery_app
from app.models.announcement import Announcement

def save_announcement(db: Session, message: dict, group, matched_keywords: list):
    announcement = Announcement(
        message_content=message["text"],
        source_group_id=group.id,
        sender_info=message.get("from", {}).get("username"),
        message_timestamp=datetime.fromtimestamp(message["date"]),
    )
    announcement.keywords = matched_keywords
    db.add(announcement)
    db.commit()
    db.refresh(announcement)

    celery_app.send_task("app.core.notifications.dispatch_notification", args=[str(announcement.id)])
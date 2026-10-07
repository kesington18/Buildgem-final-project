from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.core.celery_app import celery_app
from app.models.announcement import Announcement


def _sender_label(message: dict) -> str:
    """Telegram users don't always have a @username, and sender_info is NOT NULL."""
    sender = message.get("from") or {}
    if sender.get("username"):
        return sender["username"]
    full = " ".join(p for p in (sender.get("first_name"), sender.get("last_name")) if p)
    if full:
        return full
    if message.get("sender_chat", {}).get("title"):  # anonymous group admin
        return message["sender_chat"]["title"]
    return str(sender["id"]) if sender.get("id") else "unknown"


def save_announcement(db: Session, message: dict, group, matched_keywords: list):
    announcement = Announcement(
        message_content=message["text"],
        source_group_id=group.id,
        sender_info=_sender_label(message),
        message_timestamp=datetime.fromtimestamp(message["date"], tz=timezone.utc),
    )
    announcement.keywords = matched_keywords
    db.add(announcement)
    db.commit()
    db.refresh(announcement)

    celery_app.send_task(
        "app.core.notifications.dispatch_notification", args=[str(announcement.id)]
    )

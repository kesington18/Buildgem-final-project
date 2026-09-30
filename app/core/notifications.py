from app.models.announcement import Announcement
from app.models.notification_preferences import NotificationPreferences
from app.models.notifications import Notification
from sqlalchemy.orm import Session
import uuid
from datetime import datetime
from app.core.celery_app import celery_app
from app.db.session import sessionLocal
from app.services.push_notifier import send_push


def notify_students_for_announcement(announcement: Announcement, db: Session):
    group_matches = (
        db.query(NotificationPreferences).filter(NotificationPreferences.group_id == announcement.source_group_id)
        .all()
    )

    matched_user_ids = {pref.user_id for pref in group_matches}

    for user_id in matched_user_ids:
        already_exists = db.query(Notification).filter(Notification.user_id == user_id, Notification.announcement_id == announcement.id).first()
        if already_exists:
            continue

        new_notification = Notification(
            id = uuid.uuid4(),
            user_id= user_id,
            announcement_id= announcement.id,
            is_read= False,
            created_at= datetime.utcnow()
        )
        db.add(new_notification)
        send_push.delay(str(user_id), "New Announcement", announcement.message_content[:100])

    db.commit()
    return matched_user_ids

@celery_app.task
def dispatch_notification(announcement_id: str):
    db = sessionLocal()

    try:
        announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
        if not announcement:
            return

        notify_students_for_announcement(announcement, db)
    finally:
        db.close()
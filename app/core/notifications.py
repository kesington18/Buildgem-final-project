from app.models.announcement import Announcement
from app.models.notification_preferences import NotificationPreferences
from app.models.notifications import Notification
from sqlalchemy.orm import Session
import uuid
from datetime import datetime
from app.core.celery_app import celery_app
from app.db.session import sessionLocal
from pywebpush import webpush, WebPushException
from app.models.push_notification import PushSubscription
from app.config import settings
import json


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
        send_push(user_id, "New Announcement", announcement.message_content[:100], db)

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

# push notification
def send_push(user_id, title, body, db):
    subs = db.query(PushSubscription).filter(user_id=user_id).all()
    for sub in subs:
        try:
            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {
                        "p256dh": sub.p256dh,
                        "auth": sub.auth_key,
                    },
                },
                data=json.dumps({
                    "title": title,
                    "body": body
                }),
                vapid_private_key=settings.vapid_private_key,
                vapid_claims={"sub": "mailto:you@example.com"},
            )
        except WebPushException:
            db.delete(sub)
            db.commit()
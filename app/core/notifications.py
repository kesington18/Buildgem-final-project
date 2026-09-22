from app.models.announcement import Announcement, announcement_keywords
from app.models.notification_preferences import NotificationPreferences
from app.models.notifications import Notification
from app.models.keyword import Keyword
from sqlalchemy.orm import Session
import uuid
from datetime import datetime
from app.core.celery_app import celery_app
from app.db.session import sessionLocal


def notify_students_for_announcement(announcement: Announcement, db: Session):
    matched_keywords = (
                        db.query(Keyword)
                        .join(announcement_keywords, Keyword.id == announcement_keywords.c.keyword_id)
                        .filter(announcement_keywords.c.announcement_id == announcement.id)
                        .all()
    )

    matched_keyword_ids = [k.id for k in matched_keywords]
    matched_categories = [k.category for k in matched_keywords]


    group_matches = db.query(NotificationPreferences).filter(
        NotificationPreferences.group_id == announcement.source_group_id
        ).all()

    keyword_matches = db.query(NotificationPreferences).filter(
        NotificationPreferences.keyword_id.in_(matched_keyword_ids)
    ).all()

    category_matches = db.query(NotificationPreferences).filter(
        NotificationPreferences.category.in_(matched_categories)
    ).all()


    group_user_ids = [pref.user_id for pref in group_matches]
    keyword_user_ids = [pref.user_id for pref in keyword_matches]
    category_user_ids = [pref.user_id for pref in category_matches]

    matched_user_ids = set(group_user_ids + keyword_user_ids + category_user_ids)


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

    db.commit()


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
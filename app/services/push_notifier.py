import json
from sqlalchemy.orm import Session
from pywebpush import webpush, WebPushException

from app.core.celery_app import celery_app
from app.db.session import sessionLocal
from app.models.push_notification import PushSubscription
from app.config import settings


# push notification
@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def send_push(self, user_id: str, title: str, body: str):
        db: Session = sessionLocal()
        try:
            subs = db.query(PushSubscription).filter_by(user_id=user_id).all()
            for sub in subs:
                try:
                    webpush(
                        subscription_info={
                            "endpoint": sub.endpoint,
                            "keys": {
                                "p256dh": sub.p256dh_key,
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
        finally:
            db.close()
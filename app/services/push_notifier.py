import json
import logging

from pywebpush import webpush, WebPushException
from sqlalchemy.orm import Session

from app.config import settings
from app.core.celery_app import celery_app
from app.db.session import sessionLocal
from app.models.push_notification import PushSubscription

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def send_push(self, user_id: str, title: str, body: str, url: str = "/app/notifications", tag: str | None = None):
    """Send a web push to every device this user has enabled alerts on."""
    if not settings.vapid_private_key:  # push not configured; in-app feed still works
        return

    db: Session = sessionLocal()
    retry_error = None
    try:
        subs = db.query(PushSubscription).filter_by(user_id=user_id).all()
        for sub in subs:
            try:
                webpush(
                    subscription_info={
                        "endpoint": sub.endpoint,
                        "keys": {"p256dh": sub.p256dh_key, "auth": sub.auth_key},
                    },
                    data=json.dumps({"title": title, "body": body, "url": url, "tag": tag}),
                    vapid_private_key=settings.vapid_private_key,
                    vapid_claims={"sub": f"mailto:{settings.vapid_contact_email}"},
                )
            except WebPushException as exc:
                status = getattr(getattr(exc, "response", None), "status_code", None)
                if status in (404, 410):  # the browser unsubscribed: remove it for good
                    db.delete(sub)
                    db.commit()
                else:  # push service hiccup: keep the subscription and retry the task
                    logger.warning("Push failed for subscription %s (status %s): %s", sub.id, status, exc)
                    retry_error = exc
    finally:
        db.close()

    if retry_error is not None:
        raise self.retry(exc=retry_error)

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.config import settings
from app.db.session import get_db
from app.models.group import TelegramGroup
from app.models.notification_preferences import NotificationPreferences
from app.models.notifications import Notification
from app.models.push_notification import PushSubscription
from app.models.announcement import Announcement
from app.models.user import User
from app.schemas.notification import (
    NotificationOut,
    NotificationPreferencesOut,
    NotificationPreferenceUpdate,
    PushSubscriptionCreate,
    ReadNotification,
)

router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])


@router.get("", response_model=list[NotificationOut])
def get_current_student_notifications(
    unread_only: bool = False,
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        db.query(Notification)
        .options(selectinload(Notification.announcement).selectinload(Announcement.keywords))
        .filter(Notification.user_id == current_user.id)
    )
    if unread_only:
        query = query.filter(Notification.is_read.is_(False))
    return query.order_by(Notification.created_at.desc()).limit(limit).all()


@router.post("/read-all")
def mark_all_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    updated = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id, Notification.is_read.is_(False))
        .update({"is_read": True}, synchronize_session=False)
    )
    db.commit()
    return {"updated": updated}


@router.patch("/{id}/read", response_model=NotificationOut)
def read_notification(
    id: uuid.UUID,
    read: ReadNotification,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notification = db.query(Notification).filter(Notification.id == id).first()
    # Same 404 for "missing" and "not yours" so IDs can't be probed.
    if not notification or notification.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.is_read = read.is_read
    db.commit()
    db.refresh(notification)
    return notification


@router.get("/preferences", response_model=list[NotificationPreferencesOut])
def get_notification_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(NotificationPreferences).filter(NotificationPreferences.user_id == current_user.id).all()


@router.put("/preferences", response_model=list[NotificationPreferencesOut])
def update_preferences(
    preferences: NotificationPreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    group_ids = set(preferences.group_ids)  # de-duplicate
    if group_ids:
        valid = {
            g.id for g in db.query(TelegramGroup.id)
            .filter(TelegramGroup.id.in_(group_ids), TelegramGroup.is_active.is_(True))
            .all()
        }
        if valid != group_ids:
            raise HTTPException(status_code=400, detail="One or more groups do not exist or are not approved")

    # Replace atomically: one commit, so a failure can't leave the user with no subscriptions.
    db.query(NotificationPreferences).filter(NotificationPreferences.user_id == current_user.id).delete()
    created = [
        NotificationPreferences(id=uuid.uuid4(), user_id=current_user.id, group_id=gid, channel=preferences.channel)
        for gid in group_ids
    ]
    db.add_all(created)
    db.commit()
    for pref in created:
        db.refresh(pref)
    return created


@router.get("/vapid-public-key")
def vapid_public_key():
    """The browser needs this public key to create a web-push subscription."""
    return {"public_key": settings.vapid_public_key}


@router.post("/push-subscription")
def register_push_subscription(
    subscription: PushSubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = db.query(PushSubscription).filter_by(endpoint=subscription.endpoint).first()
    if existing:
        if existing.user_id != current_user.id:  # same browser, different account logged in
            existing.user_id = current_user.id
            db.commit()
        return {"id": str(existing.id), "endpoint": existing.endpoint}

    new_sub = PushSubscription(
        id=uuid.uuid4(),
        user_id=current_user.id,
        endpoint=subscription.endpoint,
        p256dh_key=subscription.keys.p256dh,
        auth_key=subscription.keys.auth,
    )
    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)
    return {"id": str(new_sub.id), "endpoint": new_sub.endpoint}

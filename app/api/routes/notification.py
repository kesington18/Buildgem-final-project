
from fastapi import Depends, APIRouter, HTTPException
from starlette import endpoints

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.notifications import Notification
from app.models.push_notification import PushSubscription
from app.models.notification_preferences import NotificationPreferences
from sqlalchemy.orm import Session
from app.schemas.notification import NotificationOut, ReadNotification, NotificationPreferencesOut, NotificationPreferenceUpdate, PushSubscriptionCreate
import uuid

router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])

@router.get("", response_model=list[NotificationOut])
def get_current_student_notifications(
        db:Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    current_student_notification= db.query(Notification).filter(Notification.user_id == current_user.id).all()
    return current_student_notification


@router.patch("/{id}/read",response_model=NotificationOut)
def read_notification(
        id: uuid.UUID,
        read: ReadNotification,
        db:Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    pending_notification = db.query(Notification).filter(Notification.id == id).first()
    if not pending_notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    

    if pending_notification.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Action not authorized")

    pending_notification.is_read = read.is_read
    db.commit()
    db.refresh(pending_notification)
    return pending_notification


@router.get("/preferences", response_model=list[NotificationPreferencesOut])
def get_notification_preferences(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    notification_preferences = db.query(NotificationPreferences).filter(NotificationPreferences.user_id == current_user.id).all()
    return notification_preferences

@router.put("/preferences", response_model=list[NotificationPreferencesOut])
def update_preferences(
        preferences: NotificationPreferenceUpdate,
        db:Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    current_student_preferences= db.query(NotificationPreferences).filter(NotificationPreferences.user_id == current_user.id).delete()
    db.commit()

    all_created_preferences = []

    current_user_group_preference = preferences.group_ids
    for item in current_user_group_preference or []:
        new_preference = NotificationPreferences(
            id= uuid.uuid4(),
            user_id= current_user.id,
            group_id= item,
            channel= preferences.channel,
        )
        db.add(new_preference)
        all_created_preferences.append(new_preference)

    db.commit()
    for preference in all_created_preferences:
        db.refresh(preference)
    return all_created_preferences

@router.post("/push-subscription")
def register_push_subscription(
        subscription: PushSubscriptionCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    existing = db.query(PushSubscription).filter_by(endpoint=subscription.endpoint).first()
    if existing:
        return existing

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
    return new_sub
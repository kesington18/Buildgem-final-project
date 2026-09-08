
from fastapi import Depends, APIRouter, HTTPException
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.notifications import Notification
from app.models.notification_preferences import NotificationPreferences
from sqlalchemy.orm import Session
from app.schemas.notification import NotificationOut, ReadNotification, NotificationPreferencesOut, NotificationPreferenceUpdate
import uuid

router = APIRouter(prefix="/notifications", tags=["Notifications"])

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
            keyword_id= None,
            category= None,
            channel= preferences.channel,
        )
        db.add(new_preference)
        all_created_preferences.append(new_preference)

    current_user_keyword_preference = preferences.keyword_ids
    for i in current_user_keyword_preference or []:
        new_preference = NotificationPreferences(
            id=uuid.uuid4(),
            user_id=current_user.id,
            group_id=None,
            keyword_id=i,
            category=None,
            channel=preferences.channel,
        )
        db.add(new_preference)
        all_created_preferences.append(new_preference)

    current_user_category_preference = preferences.categories
    for c in current_user_category_preference or []:
        new_preference = NotificationPreferences(
            id=uuid.uuid4(),
            user_id= current_user.id,
            group_id=None,
            keyword_id=None,
            category=c,
            channel=preferences.channel,
        )
        db.add(new_preference)
        all_created_preferences.append(new_preference)


    db.commit()
    for preference in all_created_preferences:
        db.refresh(preference)
    return all_created_preferences






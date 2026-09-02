from sqlalchemy.sql.operators import contains

from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.models import group
from app.models.group import TelegramGroup

@celery_app.task
def process_update(payload: dict):
    db = SessionLocal()

    try:
        if "my_chat_member" in payload:
            handle_chat_member_update(payload["my_chat_member"], db)
        elif "message" in payload:
            handle_message(payload["message"], db)
    finally:
        db.close()


def handle_chat_member_update(chat_member_update: dict, db):
    new_status = chat_member_update["new_chat_member"]["status"]
    chat = chat_member_update["chat"]

    if new_status in ("member", "administrator"):
        existing = db.query(TelegramGroup).filter(chat_id=chat["id"]).first()
        if not existing:
            group = TelegramGroup(
                chat_id=chat["id"],
                name=chat.get("title", "Unknown Group"),
                is_active=False,
            )
            db.add(group)
            db.commit()

def handle_message(message: dict, db):
    chat_id = message["chat"]["id"]
    text = message.get("text")

    if not text:
        return

    group = db.query(TelegramGroup).filter(chat_id=chat_id, is_active=True).first()
    if not group:
        return

    keywords = get_active_keywords(db)
    if contains_keyword(text, keywords):
        save_announcement(db, message, group)
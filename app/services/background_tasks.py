from app.core.celery_app import celery_app
from app.db.session import sessionLocal
from app.models.group import TelegramGroup
from app.services.announcement_writer import save_announcement
from app.services.group_claim import handle_claim_command
from app.services.keyword_matcher import get_active_keywords, get_matched_keywords

GROUP_CHAT_TYPES = ("group", "supergroup")

@celery_app.task
def process_update(payload: dict):
    db = sessionLocal()
    try:
        if "my_chat_member" in payload:
            handle_chat_member_update(payload["my_chat_member"], db)
        elif "message" in payload:
            handle_message(payload["message"], db)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def _telegram_display_name(user: dict) -> str | None:
    if not user:
        return None
    if user.get("username"):
        return f"@{user['username']}"
    full = " ".join(p for p in (user.get("first_name"), user.get("last_name")) if p)
    return full or None

def handle_chat_member_update(chat_member_update: dict, db):
    """The bot's own membership changed (added to / removed from a chat)."""
    chat = chat_member_update["chat"]
    # Ignore private chats (fires when someone starts/blocks the bot) and channels.
    if chat.get("type", "group") not in GROUP_CHAT_TYPES:
        return

    new_status = chat_member_update["new_chat_member"]["status"]
    actor = chat_member_update.get("from") or {}  # the Telegram user who made the change
    existing = db.query(TelegramGroup).filter_by(chat_id=chat["id"]).first()

    if new_status in ("member", "administrator"):
        if existing:
            existing.name = chat.get("title", existing.name)
            db.commit()
            return
        db.add(TelegramGroup(
            chat_id=chat["id"],
            name=chat.get("title", "Unknown Group"),
            is_active=False,  # stays pending until a dashboard admin approves it
            telegram_added_by_id=actor.get("id"),
            telegram_added_by_name=_telegram_display_name(actor),
        ))
        db.commit()

    elif new_status in ("left", "kicked") and existing and existing.is_active:
        # Bot was removed: stop treating the group as monitored.
        existing.is_active = False
        db.commit()

def handle_message(message: dict, db):
    chat_id = message["chat"]["id"]

    # A group upgraded to a supergroup gets a new chat_id; follow it.
    new_chat_id = message.get("migrate_to_chat_id")
    if new_chat_id:
        group = db.query(TelegramGroup).filter_by(chat_id=chat_id).first()
        if group:
            group.chat_id = new_chat_id
            db.commit()
        return

    text = message.get("text")
    if not text:
        return

    first_word = text.split(maxsplit=1)[0] if text.strip() else ""
    if first_word.split("@")[0].lower() == "/claim":  # /claim@BotName also works
        handle_claim_command(message, db)
        return

    group = db.query(TelegramGroup).filter_by(chat_id=chat_id, is_active=True).first()
    if not group:
        return

    keywords = get_active_keywords(db, group.id)
    matched = get_matched_keywords(text, keywords)
    if matched:
        save_announcement(db, message, group, matched)
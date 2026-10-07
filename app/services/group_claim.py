import logging
import secrets
from datetime import datetime, timedelta, timezone

from app.models.group import TelegramGroup
from app.models.group_claim import GroupClaimCode
from app.services.telegram_client import get_chat_member, send_message

logger = logging.getLogger(__name__)

GROUP_CHAT_TYPES = ("group", "supergroup")
CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # no 0/O/1/I to avoid typos
CODE_TTL = timedelta(minutes=15)


def new_claim_code() -> str:
    return "".join(secrets.choice(CODE_ALPHABET) for _ in range(8))


def _reply(chat_id: int, text: str) -> None:
    try:
        send_message(chat_id, text)
    except Exception:  # a failed reply must never break ingestion
        logger.exception("Could not send claim reply to chat %s", chat_id)


def handle_claim_command(message: dict, db) -> None:
    """`/claim CODE` posted in a group: link the group to the website account that made CODE,
    but only if the sender is genuinely a creator/admin of that Telegram group."""
    chat = message["chat"]
    chat_id = chat["id"]
    sender = message.get("from") or {}

    if chat.get("type", "group") not in GROUP_CHAT_TYPES:
        _reply(chat_id, "Send /claim inside your class group, not in a private chat.")
        return
    if message.get("sender_chat") or sender.get("is_bot"):  # anonymous admin: identity is hidden
        _reply(chat_id, "Turn off 'Remain anonymous' for your admin account, then send /claim again.")
        return

    parts = message["text"].split(maxsplit=1)
    code = parts[1].strip().upper() if len(parts) > 1 else ""
    now = datetime.now(timezone.utc)
    claim = db.query(GroupClaimCode).filter_by(code=code).first() if code else None
    if not claim or claim.used_at or claim.expires_at < now:
        _reply(chat_id, "That code is invalid or has expired. Generate a new one on the website.")
        return

    try:
        status = (get_chat_member(chat_id, sender["id"]).get("result") or {}).get("status")
    except Exception:
        logger.exception("getChatMember failed for chat %s", chat_id)
        _reply(chat_id, "I couldn't verify your admin status right now. Please try again.")
        return
    if status not in ("creator", "administrator"):
        _reply(chat_id, "Only a group admin can link this group.")
        return

    group = db.query(TelegramGroup).filter_by(chat_id=chat_id).first()
    if group and group.owner_id and group.owner_id != claim.user_id:
        _reply(chat_id, "This group is already linked to another account.")
        return
    if not group:  # bot was added but we never saw the my_chat_member update
        group = TelegramGroup(chat_id=chat_id, name=chat.get("title", "Unknown Group"))
        db.add(group)

    group.owner_id = claim.user_id
    group.is_active = True
    group.approved_by = claim.user_id
    group.approved_at = now
    if group.telegram_added_by_id is None:
        group.telegram_added_by_id = sender.get("id")
    claim.used_at = now
    db.commit()
    _reply(chat_id, "Group linked. Its owner can now manage keywords and announcements on the website.")

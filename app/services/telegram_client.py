import requests
from app.config import settings

TELEGRAM_API_BASE = f"https://api.telegram.org/bot{settings.telegram_bot_token}"

# Only the update types we actually handle.
ALLOWED_UPDATES = ["message", "my_chat_member"]


def set_webhook(url: str):
    response = requests.post(
        f"{TELEGRAM_API_BASE}/setWebhook",
        json={
            "url": url,
            "secret_token": settings.telegram_secret_token,
            "allowed_updates": ALLOWED_UPDATES,
        },
        timeout=15,
    )
    return response.json()


def get_webhook_info():
    response = requests.get(f"{TELEGRAM_API_BASE}/getWebhookInfo", timeout=15)
    return response.json()


def send_message(chat_id: int, text: str):
    response = requests.post(
        f"{TELEGRAM_API_BASE}/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=15,
    )
    return response.json()


def get_chat_member(chat_id: int, user_id: int):
    """Used to verify that someone claiming a group is really one of its admins."""
    response = requests.get(
        f"{TELEGRAM_API_BASE}/getChatMember",
        params={
            "chat_id": chat_id,
            "user_id": user_id
        },
        timeout=15,
    )
    return response.json()

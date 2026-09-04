import requests
from app.config import settings

TELEGRAM_API_BASE = f"https://api.telegram.org/bot{settings.telegram_bot_token}"


def set_webhook(url: str):
    response = requests.post(
        f"{TELEGRAM_API_BASE}/setWebhook",
        json={"url": url, "secret_token": settings.telegram_secret_token},
    )
    return response.json()


def get_webhook_info():
    response = requests.get(f"{TELEGRAM_API_BASE}/getWebhookInfo")
    return response.json()


def send_message(chat_id: int, text: str):
    response = requests.post(
        f"{TELEGRAM_API_BASE}/sendMessage",
        json={"chat_id": chat_id, "text": text},
    )
    return response.json()
import hmac

from fastapi import APIRouter, HTTPException, Header, Request

from app.config import settings
from app.services.background_tasks import process_update

telegram_router = APIRouter(tags=["telegram"])


@telegram_router.post("/webhook/telegram")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str = Header(None),
):
    supplied = (x_telegram_bot_api_secret_token or "").encode()
    expected = settings.telegram_secret_token.encode()
    if not hmac.compare_digest(supplied, expected):  # constant-time comparison
        raise HTTPException(status_code=403, detail="Invalid secret token")

    payload = await request.json()
    process_update.delay(payload)
    return {"ok": True}

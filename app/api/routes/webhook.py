import json
from fastapi import APIRouter, HTTPException, Header, Request
from app.services.background_tasks import process_update
from app.config import settings

telegram_router = APIRouter(tags=["telegram"])

@telegram_router.post("/webhook/telegram")
async def telegram_webhook(request: Request, x_telegram_bot_api_secret_token: str = Header(None)):
    if x_telegram_bot_api_secret_token != settings.telegram_secret_token:
        raise HTTPException(status_code=403, detail="Invalid secret token")

    payload = await request.json()
    with open("/code/last_payload.json", "w") as f:
        json.dump(payload, f, indent=2)
    process_update.delay(payload)
    return {
        "ok": True,
    }

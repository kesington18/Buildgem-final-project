from urllib import response

from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)

def test_webhook_rejects_wrong_secret_token():
    response = client.post(
        "/webhook/telegram",
        json={"message": {"text": "hello"}},
        headers={"X-Telegram-Bot-Api-Secret-Token": "wrong-token"},
    )
    assert response.status_code == 403

def test_webhook_accepts_correct_secret_token_and_queues_task():
    with patch("app.api.routes.webhook.process_update") as mock_task, \
        patch("app.api.routes.webhook.settings") as mock_settings:
        mock_settings.telegram_secret_token = "real-secret"
        response = client.post(
            "/webhook/telegram",
            json={"message": {"text": "hello"}},
            headers={"X-Telegram-Bot-Api-Secret-Token": "real-secret"},
        )

    assert response.status_code == 200
    assert response.json() == {
        "ok": True,
    }
    mock_task.delay.assert_called_once()
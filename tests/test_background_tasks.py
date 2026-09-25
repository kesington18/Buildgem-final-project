from unittest.mock import MagicMock, patch
from app.services.background_tasks import handle_chat_member_update,handle_message

def test_handle_chat_member_update_creates_group_when_new():
    mock_db = MagicMock()
    mock_db.query.return_value.filter_by.return_value.first.return_value = None

    payload = {
        "new_chat_member": {"status": "member"},
        "chat": {"id": -12345, "title": "Test Group"},
    }

    handle_chat_member_update(payload, mock_db)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

def test_handle_chat_member_update_skips_if_group_already_exists():
    mock_db = MagicMock()
    mock_db.query.return_value.filter_by.return_value.first.return_value = MagicMock()

    payload = {
        "new_chat_member": {"status": "member"},
        "chat": {"id": -12345, "title": "Test Group"},
    }

    handle_chat_member_update(payload, mock_db)

    mock_db.add.assert_not_called()

def test_handle_message_skips_if_group_not_authorized():
    mock_db = MagicMock()
    mock_db.query.return_value.filter_by.return_value.first.return_value = None

    message = {"chat": {"id": -12345}, "text": "venue changed"}

    with patch("app.services.background_tasks.save_announcement") as mock_save:
        handle_message(message, mock_db)

    mock_save.assert_not_called()

def test_handle_message_saves_when_authorized_and_matched():
    mock_db = MagicMock()
    mock_db.query.return_value.filter_by.return_value.first.return_value = MagicMock()

    message = {"chat": {"id": -12345}, "text": "venue changed"}

    with patch("app.services.background_tasks.get_active_keywords", return_value=["venue"]), \
            patch("app.services.background_tasks.get_matched_keywords", return_value=[MagicMock()]), \
            patch("app.services.background_tasks.save_announcement") as mock_save:
        handle_message(message, mock_db)

    mock_save.assert_called_once()
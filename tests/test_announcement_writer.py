from email import message
from unittest.mock import MagicMock, patch
from app.services.announcement_writer import save_announcement

def test_save_announcement_commits_and_links_keywords():
    mock_db = MagicMock()
    mock_group = MagicMock(id="group-uuid-123")
    mock_keywords = [MagicMock(), MagicMock()]
    message = {
        "text": "The venue has changed",
        "from": {"username": "someuser"},
        "date": 1723456789,
    }

    with patch("app.services.announcement_writer.celery_app") as mock_celery:
        save_announcement(mock_db, message, mock_group, mock_keywords)
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()
    mock_celery.send_task.assert_called_once()

    added_announcement = mock_db.add.call_args[0][0]
    assert added_announcement.message_content == "The venue has changed"
    assert added_announcement.keywords == mock_keywords
"""Covers: bot-added -> pending group (with Telegram adder), admin approval audit,
bot removed, student feed hides archived, admin delete with notifications,
and sender fallback when the Telegram user has no @username."""
from datetime import datetime, timezone
from unittest.mock import patch

from app.models.announcement import Announcement, AnnouncementStatus
from app.models.group import TelegramGroup
from app.models.notifications import Notification
from app.services.announcement_writer import save_announcement
from app.services.background_tasks import handle_chat_member_update


def _bot_added_payload(chat_id=-1001, chat_type="supergroup"):
	return {
		"chat": {"id": chat_id, "title": "CSC 200L", "type": chat_type},
		"from": {"id": 4242, "first_name": "Ada", "username": "ada_admin"},
		"new_chat_member": {"status": "member"},
	}


def test_bot_added_creates_pending_group_and_records_telegram_adder(db_session):
	handle_chat_member_update(_bot_added_payload(), db_session)

	group = db_session.query(TelegramGroup).filter_by(chat_id=-1001).one()
	assert group.is_active is False
	assert group.telegram_added_by_id == 4242
	assert group.telegram_added_by_name == "@ada_admin"
	assert group.approved_by is None


def test_private_chat_is_ignored(db_session):
	handle_chat_member_update(_bot_added_payload(chat_id=555, chat_type="private"), db_session)
	assert db_session.query(TelegramGroup).count() == 0


def test_bot_removed_deactivates_active_group(db_session):
	db_session.add(TelegramGroup(chat_id=-1002, name="G", is_active=True))
	db_session.commit()

	payload = _bot_added_payload(chat_id=-1002)
	payload["new_chat_member"] = {"status": "kicked"}
	handle_chat_member_update(payload, db_session)

	db_session.expire_all()
	assert db_session.query(TelegramGroup).filter_by(chat_id=-1002).one().is_active is False


def test_approving_group_records_dashboard_admin(client, db_session, register_and_login):
	headers = register_and_login("approver@example.com", make_admin=True)
	admin_id = client.get("/api/v1/auth/me", headers=headers).json()["id"]
	handle_chat_member_update(_bot_added_payload(chat_id=-1003), db_session)
	group = db_session.query(TelegramGroup).filter_by(chat_id=-1003).one()

	resp = client.patch(f"/api/v1/admin/groups/{group.id}", json={"is_active": True}, headers=headers)

	assert resp.status_code == 200
	body = resp.json()
	assert body["is_active"] is True
	assert body["approved_by"] == admin_id
	assert body["approved_at"] is not None
	assert body["telegram_added_by_name"] == "@ada_admin"


def test_student_feed_hides_archived_and_exposes_total(client, db_session, register_and_login):
	headers = register_and_login("feed-student@example.com")
	now = datetime.now(timezone.utc)
	db_session.add_all([
		Announcement(message_content="visible", sender_info="x", message_timestamp=now),
		Announcement(message_content="hidden", sender_info="x", message_timestamp=now,
		             status=AnnouncementStatus.archived),
	])
	db_session.commit()

	resp = client.get("/api/v1/announcements", headers=headers)

	assert resp.status_code == 200
	assert [a["message_content"] for a in resp.json()] == ["visible"]
	assert resp.headers["X-Total-Count"] == "1"


def test_student_cannot_see_group_telegram_ids(client, db_session, register_and_login):
	headers = register_and_login("groups-student@example.com")
	db_session.add(TelegramGroup(chat_id=-1004, name="Public", is_active=True, telegram_added_by_id=1))
	db_session.commit()

	groups = client.get("/api/v1/groups", headers=headers).json()

	assert groups and set(groups[0].keys()) == {"id", "name"}


def test_admin_can_delete_announcement_that_has_notifications(client, db_session, register_and_login):
	headers = register_and_login("del-admin@example.com", make_admin=True)
	user_id = client.get("/api/v1/auth/me", headers=headers).json()["id"]
	ann = Announcement(message_content="x", sender_info="x", message_timestamp=datetime.now(timezone.utc))
	db_session.add(ann)
	db_session.commit()
	db_session.add(Notification(user_id=user_id, announcement_id=ann.id))
	db_session.commit()

	resp = client.delete(f"/api/v1/admin/announcements/{ann.id}", headers=headers)

	assert resp.status_code == 200


def test_save_announcement_falls_back_when_sender_has_no_username(db_session):
	group = TelegramGroup(chat_id=-1005, name="G", is_active=True)
	db_session.add(group)
	db_session.commit()
	message = {
		"text": "exam moved",
		"from": {"id": 7, "first_name": "Ada", "last_name": "Lovelace"},
		"date": 1723456789,
	}

	with patch("app.services.announcement_writer.celery_app"):
		save_announcement(db_session, message, group, [])

	assert db_session.query(Announcement).one().sender_info == "Ada Lovelace"


def test_malformed_token_subject_returns_401_not_500(client):
	from app.core.security import create_access_token
	token = create_access_token("not-a-uuid", "student")

	resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})

	assert resp.status_code == 401


def test_register_never_creates_admin_and_me_reports_role(client, register_and_login):
	client.post("/api/v1/auth/register", json={
		"name": "Sneaky", "email": "sneaky@example.com", "password": "password123", "role": "admin",
	})
	headers = register_and_login("sneaky@example.com")
	assert client.get("/api/v1/auth/me", headers=headers).json()["role"] == "student"
	assert client.get("/api/v1/admin/keywords", headers=headers).status_code == 403

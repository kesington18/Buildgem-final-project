"""Claiming a group with /claim, then managing only that group."""
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from app.models.announcement import Announcement
from app.models.group import TelegramGroup
from app.models.group_claim import GroupClaimCode
from app.models.keyword import Keyword
from app.services.background_tasks import handle_message
from app.services.group_claim import handle_claim_command


def _me(client, headers):
	return client.get("/api/v1/auth/me", headers=headers).json()


def _group(db_session, chat_id, owner_id=None, active=False):
	g = TelegramGroup(chat_id=chat_id, name=f"G{chat_id}", is_active=active, owner_id=owner_id)
	db_session.add(g)
	db_session.commit()
	db_session.refresh(g)
	return g


def _claim_msg(chat_id, code, user_id=99, chat_type="supergroup", **extra):
	return {"chat": {"id": chat_id, "type": chat_type, "title": "Class"},
	        "from": {"id": user_id, "first_name": "Gov"}, "text": f"/claim {code}", **extra}


def _claim(db_session, message, status="creator"):
	with patch("app.services.group_claim.get_chat_member", return_value={"result": {"status": status}}), \
	     patch("app.services.group_claim.send_message") as reply:
		handle_claim_command(message, db_session)
	return reply


def _code(client, headers):
	return client.post("/api/v1/groups/claim-code", headers=headers).json()


def test_claim_code_endpoint_returns_command_and_replaces_old_code(client, register_and_login):
	headers = register_and_login("gov0@example.com")
	first = _code(client, headers)
	second = _code(client, headers)
	assert second["command"] == f"/claim {second['code']}" and first["code"] != second["code"]


def test_group_admin_can_claim_group_and_becomes_owner(client, db_session, register_and_login):
	headers = register_and_login("gov1@example.com")
	user_id = _me(client, headers)["id"]
	group = _group(db_session, -4001)
	code = _code(client, headers)["code"]

	_claim(db_session, _claim_msg(-4001, code))

	db_session.expire_all()
	group = db_session.get(TelegramGroup, group.id)
	assert str(group.owner_id) == user_id and group.is_active is True and str(group.approved_by) == user_id
	assert _me(client, headers)["is_group_owner"] is True
	assert [g["id"] for g in client.get("/api/v1/groups/mine", headers=headers).json()] == [str(group.id)]


def test_claim_creates_group_row_if_bot_join_was_missed(client, db_session, register_and_login):
	headers = register_and_login("gov1b@example.com")
	code = _code(client, headers)["code"]

	_claim(db_session, _claim_msg(-4002, code))

	assert db_session.query(TelegramGroup).filter_by(chat_id=-4002, is_active=True).count() == 1


def test_non_admin_cannot_claim(client, db_session, register_and_login):
	headers = register_and_login("gov2@example.com")
	_group(db_session, -4003)
	code = _code(client, headers)["code"]

	_claim(db_session, _claim_msg(-4003, code), status="member")

	assert db_session.query(TelegramGroup).filter_by(chat_id=-4003).one().owner_id is None


def test_expired_or_used_or_wrong_code_is_rejected(client, db_session, register_and_login):
	headers = register_and_login("gov3@example.com")
	_group(db_session, -4004)
	code = _code(client, headers)["code"]
	row = db_session.query(GroupClaimCode).filter_by(code=code).one()
	row.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
	db_session.commit()

	_claim(db_session, _claim_msg(-4004, code))
	_claim(db_session, _claim_msg(-4004, "WRONGCODE"))

	assert db_session.query(TelegramGroup).filter_by(chat_id=-4004).one().owner_id is None


def test_code_cannot_be_reused_and_group_cannot_be_stolen(client, db_session, register_and_login):
	g1 = register_and_login("gov4@example.com")
	g2 = register_and_login("gov5@example.com")
	owner_id = _me(client, g1)["id"]
	_group(db_session, -4005)
	_claim(db_session, _claim_msg(-4005, _code(client, g1)["code"]))

	_claim(db_session, _claim_msg(-4005, _code(client, g2)["code"]))  # someone else tries

	db_session.expire_all()
	assert str(db_session.query(TelegramGroup).filter_by(chat_id=-4005).one().owner_id) == owner_id


def test_anonymous_admin_and_private_chat_are_refused(client, db_session, register_and_login):
	headers = register_and_login("gov6@example.com")
	_group(db_session, -4006)
	code = _code(client, headers)["code"]

	_claim(db_session, _claim_msg(-4006, code, sender_chat={"id": -4006, "title": "Class"}))
	_claim(db_session, _claim_msg(555, code, chat_type="private"))

	assert db_session.query(TelegramGroup).filter_by(chat_id=-4006).one().owner_id is None


def test_claim_command_via_message_handler_is_not_stored_as_announcement(client, db_session, register_and_login):
	headers = register_and_login("gov7@example.com")
	_group(db_session, -4007)
	code = _code(client, headers)["code"]
	msg = _claim_msg(-4007, code)
	msg["text"] = f"/claim@MyClassBot {code}"
	msg["date"] = 1723456789

	with patch("app.services.group_claim.get_chat_member", return_value={"result": {"status": "creator"}}), \
	     patch("app.services.group_claim.send_message"):
		handle_message(msg, db_session)

	assert db_session.query(TelegramGroup).filter_by(chat_id=-4007).one().owner_id is not None
	assert db_session.query(Announcement).count() == 0


def test_owner_sees_and_manages_only_own_groups(client, db_session, register_and_login):
	a = register_and_login("own-a@example.com")
	b = register_and_login("own-b@example.com")
	ga = _group(db_session, -4008, owner_id=_me(client, a)["id"], active=True)
	gb = _group(db_session, -4009, owner_id=_me(client, b)["id"], active=True)

	listed = client.get("/api/v1/admin/groups", headers=a).json()
	assert [g["id"] for g in listed] == [str(ga.id)]
	assert client.patch(f"/api/v1/admin/groups/{ga.id}", json={"is_active": False}, headers=a).status_code == 200
	assert client.patch(f"/api/v1/admin/groups/{gb.id}", json={"is_active": False}, headers=a).status_code == 404


def test_plain_student_gets_403_on_management_routes(client, register_and_login):
	headers = register_and_login("plain@example.com")
	for path in ("/api/v1/admin/groups", "/api/v1/admin/announcements", "/api/v1/admin/analytics"):
		assert client.get(path, headers=headers).status_code == 403


def test_owner_moderates_only_own_groups_announcements(client, db_session, register_and_login):
	a = register_and_login("mod-a@example.com")
	b = register_and_login("mod-b@example.com")
	ga = _group(db_session, -4010, owner_id=_me(client, a)["id"], active=True)
	gb = _group(db_session, -4011, owner_id=_me(client, b)["id"], active=True)
	now = datetime.now(timezone.utc)
	mine = Announcement(message_content="mine", sender_info="x", message_timestamp=now, source_group_id=ga.id)
	theirs = Announcement(message_content="theirs", sender_info="x", message_timestamp=now, source_group_id=gb.id)
	db_session.add_all([mine, theirs])
	db_session.commit()

	listed = client.get("/api/v1/admin/announcements", headers=a).json()
	assert [x["message_content"] for x in listed] == ["mine"]
	assert client.patch(f"/api/v1/admin/announcements/{theirs.id}", json={"status": "archived"}, headers=a).status_code == 404
	assert client.delete(f"/api/v1/admin/announcements/{theirs.id}", headers=a).status_code == 404
	assert client.patch(f"/api/v1/admin/announcements/{mine.id}", json={"status": "archived"}, headers=a).status_code == 200

	stats = client.get("/api/v1/admin/analytics", headers=a).json()
	assert stats["per_group"] == {ga.name: 1} and stats["totals"]["announcements"] == 1


def test_bot_only_listens_for_the_groups_own_keywords(client, db_session, register_and_login):
	a = register_and_login("kw-a@example.com")
	b = register_and_login("kw-b@example.com")
	ga = _group(db_session, -4012, owner_id=_me(client, a)["id"], active=True)
	gb = _group(db_session, -4013, owner_id=_me(client, b)["id"], active=True)
	client.post(f"/api/v1/groups/{ga.id}/keywords", json={"term": "exam", "category": "academic"}, headers=a)
	msg = lambda chat_id: {"chat": {"id": chat_id}, "text": "The exam is on Friday", "date": 1723456789,
	                       "from": {"username": "someone"}}

	with patch("app.services.announcement_writer.celery_app"):
		handle_message(msg(-4013), db_session)  # group B has no 'exam' keyword
		assert db_session.query(Announcement).count() == 0
		handle_message(msg(-4012), db_session)  # group A does

	saved = db_session.query(Announcement).one()
	assert saved.source_group_id == ga.id and [k.term for k in saved.keywords] == ["exam"]

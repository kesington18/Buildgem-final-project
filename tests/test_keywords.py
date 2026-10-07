"""Keywords belong to one group. The owner manages them; other students can only suggest."""
from app.models.group import TelegramGroup
from app.models.keyword import Keyword
from app.services.keyword_matcher import get_active_keywords


def _me(client, headers):
	return client.get("/api/v1/auth/me", headers=headers).json()


def _group(db_session, chat_id=-3001, owner_id=None, active=True):
	g = TelegramGroup(chat_id=chat_id, name=f"G{chat_id}", is_active=active, owner_id=owner_id)
	db_session.add(g)
	db_session.commit()
	db_session.refresh(g)
	return g


def _url(group, suffix=""):
	return f"/api/v1/groups/{group.id}/keywords{suffix}"


def test_owner_can_create_list_update_delete_keyword(client, db_session, register_and_login):
	owner = register_and_login("owner@example.com")
	group = _group(db_session, owner_id=_me(client, owner)["id"])

	created = client.post(_url(group), json={"term": "Exam", "category": "Academic"}, headers=owner)
	assert created.status_code == 200
	body = created.json()
	assert body["term"] == "exam" and body["status"] == "approved" and body["group_id"] == str(group.id)

	assert len(client.get(_url(group), headers=owner).json()) == 1

	patched = client.patch(_url(group, f"/{body['id']}"), json={"term": "midterm", "is_active": False}, headers=owner)
	assert patched.status_code == 200 and patched.json()["term"] == "midterm" and patched.json()["is_active"] is False

	assert client.delete(_url(group, f"/{body['id']}"), headers=owner).status_code == 200
	assert client.get(_url(group), headers=owner).json() == []


def test_student_suggestion_is_pending_until_owner_approves(client, db_session, register_and_login):
	owner = register_and_login("owner2@example.com")
	student = register_and_login("student2@example.com")
	group = _group(db_session, chat_id=-3002, owner_id=_me(client, owner)["id"])

	sug = client.post(_url(group), json={"term": "quiz", "category": "academic"}, headers=student)
	assert sug.status_code == 200 and sug.json()["status"] == "pending"
	kw_id = sug.json()["id"]

	# The bot ignores it while it is pending.
	assert get_active_keywords(db_session, group.id) == []

	# The owner sees it in the review queue and approves it.
	queue = client.get(_url(group) + "?status=pending", headers=owner).json()
	assert [k["id"] for k in queue] == [kw_id]
	approved = client.patch(_url(group, f"/{kw_id}"), json={"status": "approved"}, headers=owner)
	assert approved.status_code == 200 and approved.json()["status"] == "approved"
	assert [k.term for k in get_active_keywords(db_session, group.id)] == ["quiz"]


def test_other_students_only_see_approved_plus_their_own_pending(client, db_session, register_and_login):
	owner = register_and_login("owner3@example.com")
	s1 = register_and_login("s1@example.com")
	s2 = register_and_login("s2@example.com")
	group = _group(db_session, chat_id=-3003, owner_id=_me(client, owner)["id"])
	client.post(_url(group), json={"term": "exam", "category": "academic"}, headers=owner)
	client.post(_url(group), json={"term": "s1idea", "category": "academic"}, headers=s1)

	assert sorted(k["term"] for k in client.get(_url(group), headers=s1).json()) == ["exam", "s1idea"]
	assert [k["term"] for k in client.get(_url(group), headers=s2).json()] == ["exam"]


def test_students_cannot_edit_or_delete_others_keywords(client, db_session, register_and_login):
	owner = register_and_login("owner4@example.com")
	student = register_and_login("student4@example.com")
	group = _group(db_session, chat_id=-3004, owner_id=_me(client, owner)["id"])
	kw_id = client.post(_url(group), json={"term": "exam", "category": "academic"}, headers=owner).json()["id"]

	assert client.patch(_url(group, f"/{kw_id}"), json={"is_active": False}, headers=student).status_code == 403
	assert client.delete(_url(group, f"/{kw_id}"), headers=student).status_code == 403


def test_student_can_withdraw_own_pending_suggestion(client, db_session, register_and_login):
	owner = register_and_login("owner5@example.com")
	student = register_and_login("student5@example.com")
	group = _group(db_session, chat_id=-3005, owner_id=_me(client, owner)["id"])
	kw_id = client.post(_url(group), json={"term": "lab", "category": "venue"}, headers=student).json()["id"]

	assert client.delete(_url(group, f"/{kw_id}"), headers=student).status_code == 200


def test_owner_of_one_group_cannot_manage_another_groups_keywords(client, db_session, register_and_login):
	a = register_and_login("owner-a@example.com")
	b = register_and_login("owner-b@example.com")
	group_a = _group(db_session, chat_id=-3006, owner_id=_me(client, a)["id"])
	group_b = _group(db_session, chat_id=-3007, owner_id=_me(client, b)["id"])
	kw_id = client.post(_url(group_b), json={"term": "exam", "category": "academic"}, headers=b).json()["id"]

	assert client.patch(_url(group_b, f"/{kw_id}"), json={"is_active": False}, headers=a).status_code == 403
	assert client.delete(_url(group_b, f"/{kw_id}"), headers=a).status_code == 403
	# Using group A's URL with group B's keyword id must not work either.
	assert client.delete(_url(group_a, f"/{kw_id}"), headers=a).status_code == 404


def test_same_term_allowed_in_different_groups_but_not_twice_in_one(client, db_session, register_and_login):
	a = register_and_login("dup-a@example.com")
	b = register_and_login("dup-b@example.com")
	group_a = _group(db_session, chat_id=-3008, owner_id=_me(client, a)["id"])
	group_b = _group(db_session, chat_id=-3009, owner_id=_me(client, b)["id"])
	body = {"term": "exam", "category": "academic"}

	assert client.post(_url(group_a), json=body, headers=a).status_code == 200
	assert client.post(_url(group_b), json=body, headers=b).status_code == 200
	assert client.post(_url(group_a), json=body, headers=a).status_code == 409


def test_site_admin_can_manage_any_group(client, db_session, register_and_login):
	admin = register_and_login("site-admin@example.com", make_admin=True)
	group = _group(db_session, chat_id=-3010)

	resp = client.post(_url(group), json={"term": "exam", "category": "academic"}, headers=admin)

	assert resp.status_code == 200 and resp.json()["status"] == "approved"


def test_pending_suggestions_are_capped_per_student(client, db_session, register_and_login):
	owner = register_and_login("owner6@example.com")
	student = register_and_login("student6@example.com")
	group = _group(db_session, chat_id=-3011, owner_id=_me(client, owner)["id"])

	for i in range(10):
		assert client.post(_url(group), json={"term": f"t{i}", "category": "x"}, headers=student).status_code == 200
	assert client.post(_url(group), json={"term": "t10", "category": "x"}, headers=student).status_code == 429


def test_students_cannot_touch_inactive_groups(client, db_session, register_and_login):
	student = register_and_login("student7@example.com")
	group = _group(db_session, chat_id=-3012, active=False)

	assert client.get(_url(group), headers=student).status_code == 404
	assert client.post(_url(group), json={"term": "a", "category": "b"}, headers=student).status_code == 404


def test_no_token_rejected(client, db_session):
	group = _group(db_session, chat_id=-3013)
	assert client.get(_url(group)).status_code == 401

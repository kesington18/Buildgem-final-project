from datetime import datetime, timezone

from app.models.announcement import Announcement


def create_announcement(db_session):
	announcement = Announcement(
		message_content="Original announcement",
		sender_info="sender",
		message_timestamp=datetime.now(timezone.utc),
	)
	db_session.add(announcement)
	db_session.commit()
	db_session.refresh(announcement)
	return announcement


def test_admin_can_update_announcement(client, db_session, register_and_login):
	headers = register_and_login("announcement-admin@example.com", make_admin=True)
	announcement = create_announcement(db_session)

	response = client.patch(
		f"/api/v1/admin/announcements/{announcement.id}",
		json={"message_content": "Updated announcement", "status": "archived"},
		headers=headers,
	)

	assert response.status_code == 200
	assert response.json()["message_content"] == "Updated announcement"
	assert response.json()["status"] == "archived"


def test_student_cannot_update_announcement(client, db_session, register_and_login):
	headers = register_and_login("announcement-student@example.com", make_admin=False)
	announcement = create_announcement(db_session)

	response = client.patch(
		f"/api/v1/admin/announcements/{announcement.id}",
		json={"status": "archived"},
		headers=headers,
	)

	assert response.status_code == 403


def test_update_missing_announcement_returns_404(client, register_and_login):
	headers = register_and_login("missing-update@example.com", make_admin=True)
	missing_id = "00000000-0000-0000-0000-000000000000"

	response = client.patch(
		f"/api/v1/admin/announcements/{missing_id}",
		json={"status": "archived"},
		headers=headers,
	)

	assert response.status_code == 404
	assert response.json()["detail"] == "Announcement not found"


def test_admin_can_delete_announcement(client, db_session, register_and_login):
	headers = register_and_login("announcement-delete@example.com", make_admin=True)
	announcement = create_announcement(db_session)

	response = client.delete(
		f"/api/v1/admin/announcements/{announcement.id}",
		headers=headers,
	)

	assert response.status_code == 200
	assert response.json() == {"detail": "Deleted"}
	assert db_session.get(Announcement, announcement.id) is None


def test_delete_missing_announcement_returns_404(client, register_and_login):
	headers = register_and_login("missing-delete@example.com", make_admin=True)
	missing_id = "00000000-0000-0000-0000-000000000000"

	response = client.delete(
		f"/api/v1/admin/announcements/{missing_id}",
		headers=headers,
	)

	assert response.status_code == 404
	assert response.json()["detail"] == "Announcement not found"

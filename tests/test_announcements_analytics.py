from datetime import datetime, timezone

from app.models.announcement import Announcement, announcement_keywords
from app.models.group import TelegramGroup
from app.models.keyword import Keyword


def test_admin_analytics_route_is_registered(client, register_and_login):
	headers = register_and_login("analytics-route@example.com", make_admin=True)

	response = client.get("/api/v1/admin/analytics", headers=headers)

	assert response.status_code == 200
	assert response.json() == {"per_category": {}, "per_group": {}}


def test_admin_analytics_counts_categories_and_groups(
	client,
	db_session,
	register_and_login,
):
	headers = register_and_login("analytics-data@example.com", make_admin=True)
	group = TelegramGroup(chat_id=-1009876543210, name="Analytics Group", is_active=True)
	keyword = Keyword(term="exam", category="academic", is_active=True)
	announcement = Announcement(
		message_content="The exam is on Friday.",
		sender_info="lecturer",
		message_timestamp=datetime.now(timezone.utc),
	)
	db_session.add_all([group, keyword])
	db_session.flush()
	announcement.source_group_id = group.id
	db_session.add(announcement)
	db_session.flush()
	db_session.execute(
		announcement_keywords.insert().values(
			announcement_id=announcement.id,
			keyword_id=keyword.id,
		)
	)
	db_session.commit()

	response = client.get("/api/v1/admin/analytics", headers=headers)

	assert response.status_code == 200
	assert response.json() == {
		"per_category": {"academic": 1},
		"per_group": {"Analytics Group": 1},
	}


def test_student_cannot_access_admin_analytics(client, register_and_login):
	headers = register_and_login("analytics-student@example.com", make_admin=False)

	response = client.get("/api/v1/admin/analytics", headers=headers)

	assert response.status_code == 403

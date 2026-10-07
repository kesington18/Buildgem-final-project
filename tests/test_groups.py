def test_admin_can_create_group_as_inactive(client, register_and_login):
	headers = register_and_login("group-admin@example.com", make_admin=True)

	response = client.post(
		"/api/v1/admin/groups",
		json={"chat_id": -1001234567890, "name": "Pending Group"},
		headers=headers,
	)

	assert response.status_code == 200
	assert response.json()["is_active"] is False


def test_admin_can_authorize_group(client, register_and_login):
	headers = register_and_login("authorize-group@example.com", make_admin=True)
	create_response = client.post(
		"/api/v1/admin/groups",
		json={"chat_id": -1001234567891, "name": "Pending Group"},
		headers=headers,
	)
	group_id = create_response.json()["id"]

	response = client.patch(
		f"/api/v1/admin/groups/{group_id}",
		json={"is_active": True},
		headers=headers,
	)

	assert response.status_code == 200
	assert response.json()["is_active"] is True


def test_student_cannot_access_groups(client, register_and_login):
	headers = register_and_login("group-student@example.com", make_admin=False)

	response = client.get("/api/v1/admin/groups", headers=headers)

	assert response.status_code == 403


def test_missing_group_returns_404(client, register_and_login):
	headers = register_and_login("missing-group@example.com", make_admin=True)
	missing_id = "00000000-0000-0000-0000-000000000000"

	response = client.patch(
		f"/api/v1/admin/groups/{missing_id}",
		json={"is_active": True},
		headers=headers,
	)

	assert response.status_code == 404

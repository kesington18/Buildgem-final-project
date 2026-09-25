def test_admin_can_create_and_list_keyword(client, register_and_login):
    headers = register_and_login("admin1@example.com", make_admin=True)

    resp = client.post("/api/v1/admin/keywords", json={"term": "exam", "category": "academic"}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["term"] == "exam"

    resp = client.get("/api/v1/admin/keywords", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_student_cannot_access_keywords(client, register_and_login):
    headers = register_and_login("student1@example.com", make_admin=False)
    resp = client.get("/api/v1/admin/keywords", headers=headers)
    assert resp.status_code == 403


def test_no_token_rejected(client):
    resp = client.get("/api/v1/admin/keywords")
    assert resp.status_code == 401


def test_update_keyword(client, register_and_login):
    headers = register_and_login("admin2@example.com", make_admin=True)
    create = client.post("/api/v1/admin/keywords", json={"term": "deadline", "category": "academic"}, headers=headers)
    kw_id = create.json()["id"]

    resp = client.patch(f"/api/v1/admin/keywords/{kw_id}", json={"is_active": False}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


def test_update_nonexistent_keyword_404(client, register_and_login):
    headers = register_and_login("admin3@example.com", make_admin=True)
    fake_id = "00000000-0000-0000-0000-000000000000"
    resp = client.patch(f"/api/v1/admin/keywords/{fake_id}", json={"is_active": False}, headers=headers)
    assert resp.status_code == 404


def test_delete_keyword(client, register_and_login):
    headers = register_and_login("admin4@example.com", make_admin=True)
    create = client.post("/api/v1/admin/keywords", json={"term": "football", "category": "sports"}, headers=headers)
    kw_id = create.json()["id"]

    resp = client.delete(f"/api/v1/admin/keywords/{kw_id}", headers=headers)
    assert resp.status_code == 200

    resp = client.get("/api/v1/admin/keywords", headers=headers)
    assert len(resp.json()) == 0

def test_keyword_term_and_category_lowercased(client, register_and_login):
    headers = register_and_login("admin5@example.com", make_admin=True)
    resp = client.post("/api/v1/admin/keywords", json={"term": "EXAM", "category": "Academic"}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["term"] == "exam"
    assert resp.json()["category"] == "academic"
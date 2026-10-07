def test_register_success(client):
    resp = client.post("/api/v1/auth/register", json={
        "name": "Alice", "email": "alice@example.com", "password": "secret123",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == "alice@example.com"
    assert body["role"] == "student"
    assert "password" not in body
    assert "password_hash" not in body


def test_register_duplicate_email_fails(client):
    client.post("/api/v1/auth/register", json={
        "name": "Alice", "email": "dup@example.com", "password": "secret123",
    })
    resp = client.post("/api/v1/auth/register", json={
        "name": "Alice 2", "email": "dup@example.com", "password": "secret456",
    })
    assert resp.status_code == 400


def test_login_success(client):
    client.post("/api/v1/auth/register", json={
        "name": "Bob", "email": "bob@example.com", "password": "secret123",
    })
    resp = client.post("/api/v1/auth/login", json={
        "email": "bob@example.com", "password": "secret123",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


def test_login_wrong_password_fails(client):
    client.post("/api/v1/auth/register", json={
        "name": "Carl", "email": "carl@example.com", "password": "correctpass",
    })
    resp = client.post("/api/v1/auth/login", json={
        "email": "carl@example.com", "password": "wrongpass",
    })
    assert resp.status_code == 401


def test_login_nonexistent_user_fails(client):
    resp = client.post("/api/v1/auth/login", json={
        "email": "ghost@example.com", "password": "whatever",
    })
    assert resp.status_code == 401


def test_refresh_with_valid_token(client):
    client.post("/api/v1/auth/register", json={
        "name": "Dana", "email": "dana@example.com", "password": "secret123",
    })
    login_resp = client.post("/api/v1/auth/login", json={
        "email": "dana@example.com", "password": "secret123",
    })
    refresh_token = login_resp.json()["refresh_token"]
    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_refresh_with_garbage_token_fails(client):
    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": "not-a-real-token"})
    assert resp.status_code == 401

def test_form_token_endpoint_works_for_swagger(client):
    client.post("/api/v1/auth/register", json={
        "name": "Swag", "email": "swag@example.com", "password": "secret123",
    })
    resp = client.post("/api/v1/auth/token", data={"username": "swag@example.com", "password": "secret123"})
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.json()["email"] == "swag@example.com"


def _login(client, email="out@example.com", password="secret123"):
    client.post("/api/v1/auth/register", json={"name": "Out", "email": email, "password": password})
    return client.post("/api/v1/auth/login", json={"email": email, "password": password}).json()


def test_logout_revokes_access_and_refresh_tokens(client):
    tokens = _login(client)
    auth = {"Authorization": f"Bearer {tokens['access_token']}"}
    assert client.get("/api/v1/auth/me", headers=auth).status_code == 200

    resp = client.post("/api/v1/auth/logout", json={"refresh_token": tokens["refresh_token"]}, headers=auth)

    assert resp.status_code == 200
    assert client.get("/api/v1/auth/me", headers=auth).status_code == 401
    assert client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}).status_code == 401


def test_logout_only_ends_that_session(client):
    first = _login(client, "multi@example.com")
    second = _login(client, "multi@example.com")
    client.post("/api/v1/auth/logout", json={"refresh_token": first["refresh_token"]},
                headers={"Authorization": f"Bearer {first['access_token']}"})

    still_ok = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {second['access_token']}"})
    assert still_ok.status_code == 200


def test_logout_is_idempotent_and_tolerates_bad_or_missing_tokens(client):
    tokens = _login(client, "idem@example.com")
    auth = {"Authorization": f"Bearer {tokens['access_token']}"}
    assert client.post("/api/v1/auth/logout", json={}, headers=auth).status_code == 200
    assert client.post("/api/v1/auth/logout", json={}, headers=auth).status_code == 200
    assert client.post("/api/v1/auth/logout", json={"refresh_token": "garbage"}).status_code == 200
    assert client.post("/api/v1/auth/logout").status_code == 200


def test_logout_works_for_admins_too(client, register_and_login):
    headers = register_and_login("adminout@example.com", make_admin=True)
    assert client.get("/api/v1/admin/analytics", headers=headers).status_code == 200
    assert client.post("/api/v1/auth/logout", headers=headers).status_code == 200
    assert client.get("/api/v1/admin/analytics", headers=headers).status_code == 401

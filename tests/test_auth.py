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
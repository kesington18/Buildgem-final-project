import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://test_user:test_password@test-db:5432/test_db",
)
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("TELEGRAM_SECRET_TOKEN", "test-telegram-secret")
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "test-bot-token")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379")

from app.main import app
from app.db.session import Base, get_db

TEST_DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def register_and_login(client):
    """Helper: registers a user, promotes to admin if requested, returns headers."""
    def _make(email="test@example.com", password="testpass123", make_admin=False):
        client.post("/api/v1/auth/register", json={
            "name": "Test User", "email": email, "password": password,
        })
        if make_admin:
            from app.models.user import User, UserRole
            db = TestingSessionLocal()
            user = db.query(User).filter(User.email == email).first()
            user.role = UserRole.admin
            db.commit()
            db.close()
        resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
        token = resp.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    return _make
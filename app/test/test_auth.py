from collections.abc import Generator
from typing import Any, Dict

import pytest
from fastapi.testclient import TestClient
from google.oauth2 import id_token as google_id_token
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db import get_db
from app.db.base import Base
from app.main import app
from app.models.user import User

TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    future=True,
)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)


@pytest.fixture(autouse=True)
def setup_database() -> Generator[None, None, None]:
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    settings.GOOGLE_CLIENT_ID = "test-google-client"
    settings.GOOGLE_CLIENT_SECRET = "test-google-secret"
    settings.GOOGLE_REDIRECT_URI = "http://testserver/api/auth/google/callback"
    settings.JWT_SECRET = "test-jwt-secret"
    settings.JWT_ALGORITHM = "HS256"

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_google_login_redirect(client: TestClient) -> None:
    response = client.get("/api/auth/google/login", allow_redirects=False)
    assert response.status_code == 307
    assert "accounts.google.com" in response.headers["location"]


def test_google_callback_creates_user_and_returns_jwt(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    def mock_post(url: str, data: Dict[str, Any], timeout: int) -> Any:
        class MockResponse:
            status_code = 200

            def json(self) -> Dict[str, str]:
                return {"id_token": "fake-id-token"}

            def raise_for_status(self) -> None:
                return None

        return MockResponse()

    def mock_verify(token: str, request: Any, audience: str, clock_skew_in_seconds: int = 10) -> Dict[str, Any]:
        return {
            "email": "user@example.com",
            "name": "Test User",
            "picture": "http://picture.example.com/avatar.png",
            "sub": "google-sub-id",
        }

    monkeypatch.setattr("app.routers.auth_router.requests.post", mock_post)
    monkeypatch.setattr(google_id_token, "verify_oauth2_token", mock_verify)

    response = client.get("/api/auth/google/callback", params={"code": "test-code"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["user"]["email"] == "user@example.com"

    token = payload["access_token"]
    decoded = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    assert decoded["sub"] == "user@example.com"

    with TestingSessionLocal() as session:
        db_user = session.query(User).filter(User.email == "user@example.com").first()
        assert db_user is not None
        assert db_user.google_id == "google-sub-id"


def test_verify_endpoint_updates_existing_user(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    with TestingSessionLocal() as session:
        user = User(
            email="existing@example.com",
            name="Existing",
            picture=None,
            google_id="existing-google-id",
            is_verified=False,
        )
        session.add(user)
        session.commit()

    def mock_verify(token: str, request: Any, audience: str, clock_skew_in_seconds: int = 10) -> Dict[str, Any]:
        return {
            "email": "existing@example.com",
            "name": "Updated Name",
            "picture": "http://picture.example.com/updated.png",
            "sub": "existing-google-id",
        }

    monkeypatch.setattr(google_id_token, "verify_oauth2_token", mock_verify)

    response = client.post("/api/auth/google/verify", json={"token": "frontend-id-token"})
    assert response.status_code == 200
    body = response.json()
    assert body["user"]["name"] == "Updated Name"
    assert body["user"]["is_verified"] is True

    with TestingSessionLocal() as session:
        db_user = session.query(User).filter(User.email == "existing@example.com").first()
        assert db_user is not None
        assert db_user.name == "Updated Name"
        assert db_user.picture == "http://picture.example.com/updated.png"

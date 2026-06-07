import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.db.base import Base, get_db
from app.main import app

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def override_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def clean_database():
    Base.metadata.create_all(engine)
    app.dependency_overrides[get_db] = override_db
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def signup(client, email="demo@example.com"):
    response = client.post(
        "/api/auth/signup",
        json={"email": email, "name": "Demo User", "password": "StrongPass123!"},
    )
    assert response.status_code == 201
    return response.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_health_signup_login_and_profile(client):
    assert client.get("/health").json()["status"] == "healthy"
    token = signup(client)
    profile = client.get("/api/auth/me", headers=auth(token))
    assert profile.status_code == 200
    assert profile.json()["email"] == "demo@example.com"
    login = client.post(
        "/api/auth/login",
        json={"email": "demo@example.com", "password": "StrongPass123!"},
    )
    assert login.status_code == 200


def test_journal_crud_and_ownership(client):
    owner = signup(client, "owner@example.com")
    other = signup(client, "other@example.com")
    created = client.post(
        "/api/journals/",
        headers=auth(owner),
        json={"title": "Today", "content": "I took a useful pause.", "mood": "calm"},
    )
    assert created.status_code == 201
    journal_id = created.json()["id"]
    assert client.get(f"/api/journals/{journal_id}", headers=auth(other)).status_code == 404
    updated = client.patch(
        f"/api/journals/{journal_id}",
        headers=auth(owner),
        json={"mood": "hopeful"},
    )
    assert updated.json()["mood"] == "hopeful"
    assert client.delete(f"/api/journals/{journal_id}", headers=auth(owner)).status_code == 204


def test_mood_summary_and_fallback_reflection(client):
    token = signup(client)
    first = client.post(
        "/api/moods/",
        headers=auth(token),
        json={"mood": "calm", "intensity": 4, "note": "A steady morning."},
    )
    client.post(
        "/api/moods/",
        headers=auth(token),
        json={"mood": "calm", "intensity": 7},
    )
    summary = client.get("/api/moods/summary", headers=auth(token)).json()
    assert summary == {
        "total_check_ins": 2,
        "most_common_mood": "calm",
        "recent_mood_trend": "increasing",
    }
    reflection = client.post(
        "/api/reflections/",
        headers=auth(token),
        json={"source_type": "mood", "source_id": first.json()["id"]},
    )
    assert reflection.status_code == 200
    assert reflection.json()["source"] == "fallback"
    assert "not a replacement" in reflection.json()["disclaimer"]


def test_crisis_language_returns_safety_message(client):
    token = signup(client)
    journal = client.post(
        "/api/journals/",
        headers=auth(token),
        json={"title": "Need support", "content": "I want to hurt myself.", "mood": "low"},
    )
    reflection = client.post(
        "/api/reflections/",
        headers=auth(token),
        json={"source_type": "journal", "source_id": journal.json()["id"]},
    )
    body = reflection.json()
    assert body["crisis_detected"] is True
    assert "emergency services" in body["reflection"]


def test_resources_are_public(client):
    response = client.get("/api/resources/?category=stress")
    assert response.status_code == 200
    assert response.json()["resources"][0]["category"] == "stress"

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(
        app_module,
        "activities",
        {
            "Chess Club": {
                "description": "Learn strategies and compete in chess tournaments",
                "schedule": "Fridays, 3:30 PM - 5:00 PM",
                "max_participants": 12,
                "participants": ["existing@example.edu"],
            }
        },
    )
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_activity_data(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["existing@example.edu"],
        }
    }


def test_signup_adds_student_to_activity(client):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "new@example.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Signed up new@example.edu for Chess Club"}
    assert "new@example.edu" in client.get("/activities").json()["Chess Club"]["participants"]


def test_signup_returns_404_for_unknown_activity(client):
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "new@example.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_returns_400_for_duplicate_student(client):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "existing@example.edu"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}


def test_unregister_removes_student_from_activity(client):
    response = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": "existing@example.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Unregistered existing@example.edu from Chess Club"}
    assert "existing@example.edu" not in client.get("/activities").json()["Chess Club"]["participants"]


def test_unregister_returns_404_for_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown Club/unregister",
        params={"email": "existing@example.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_returns_400_for_unregistered_student(client):
    response = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": "missing@example.edu"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Student is not signed up for this activity"}


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"

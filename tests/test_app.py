import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
initial_activities = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def restore_activities():
    activities.clear()
    activities.update(copy.deepcopy(initial_activities))
    yield
    activities.clear()
    activities.update(copy.deepcopy(initial_activities))


def test_get_activities_returns_known_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert data["Chess Club"]["description"].startswith("Learn strategies")
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_participant():
    response = client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")

    assert response.status_code == 200
    assert response.json()["message"] == "Signed up test@mergington.edu for Chess Club"

    activities_response = client.get("/activities")
    participants = activities_response.json()["Chess Club"]["participants"]
    assert "test@mergington.edu" in participants


def test_signup_duplicate_returns_400():
    client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")
    response = client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_remove_participant_from_activity():
    response = client.delete("/activities/Chess%20Club/participants?email=michael@mergington.edu")

    assert response.status_code == 200
    assert response.json()["message"] == "Removed michael@mergington.edu from Chess Club"

    activities_response = client.get("/activities")
    participants = activities_response.json()["Chess Club"]["participants"]
    assert "michael@mergington.edu" not in participants


def test_remove_missing_participant_returns_404():
    response = client.delete("/activities/Chess%20Club/participants?email=missing@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_activity_not_found_returns_404_for_signup():
    response = client.post("/activities/Unknown%20Club/signup?email=test@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_activity_not_found_returns_404_for_remove():
    response = client.delete("/activities/Unknown%20Club/participants?email=test@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

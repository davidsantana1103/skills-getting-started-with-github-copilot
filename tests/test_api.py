from fastapi.testclient import TestClient
import pytest

from src.app import app, activities

client = TestClient(app)

TEST_ACTIVITY = "Programming Class"
TEST_EMAIL = "teststudent@mergington.edu"


def setup_function():
    # ensure test email is not present before each test
    if TEST_EMAIL in activities[TEST_ACTIVITY]["participants"]:
        activities[TEST_ACTIVITY]["participants"].remove(TEST_EMAIL)


def teardown_function():
    # clean up after tests
    if TEST_EMAIL in activities[TEST_ACTIVITY]["participants"]:
        activities[TEST_ACTIVITY]["participants"].remove(TEST_EMAIL)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert TEST_ACTIVITY in data
    assert "participants" in data[TEST_ACTIVITY]


def test_signup_for_activity():
    # signup
    resp = client.post(f"/activities/{TEST_ACTIVITY}/signup?email={TEST_EMAIL}")
    assert resp.status_code == 200
    json_data = resp.json()
    assert "Signed up" in json_data.get("message", "")

    # verify participant was added
    resp2 = client.get("/activities")
    participants = resp2.json()[TEST_ACTIVITY]["participants"]
    assert TEST_EMAIL in participants


def test_double_signup_fails():
    # first signup
    client.post(f"/activities/{TEST_ACTIVITY}/signup?email={TEST_EMAIL}")
    # second signup should fail
    resp = client.post(f"/activities/{TEST_ACTIVITY}/signup?email={TEST_EMAIL}")
    assert resp.status_code == 400


def test_unregister_participant():
    # ensure participant exists
    if TEST_EMAIL not in activities[TEST_ACTIVITY]["participants"]:
        client.post(f"/activities/{TEST_ACTIVITY}/signup?email={TEST_EMAIL}")

    # unregister
    resp = client.delete(f"/activities/{TEST_ACTIVITY}/unregister?email={TEST_EMAIL}")
    assert resp.status_code == 200
    assert "Unregistered" in resp.json().get("message", "")

    # verify removed
    resp2 = client.get("/activities")
    participants = resp2.json()[TEST_ACTIVITY]["participants"]
    assert TEST_EMAIL not in participants

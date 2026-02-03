from fastapi.testclient import TestClient
from src import app as app_module

client = TestClient(app_module.app)


def test_root_redirect():
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code == 307
    assert resp.headers["location"] == "/static/index.html"


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Basketball Team" in data


def test_signup_success_and_cleanup():
    email = "newstudent@mergington.edu"
    # ensure not already present
    participants = app_module.activities["Art Club"]["participants"]
    if email in participants:
        participants.remove(email)

    resp = client.post("/activities/Art Club/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in app_module.activities["Art Club"]["participants"]

    # cleanup to keep tests idempotent
    app_module.activities["Art Club"]["participants"].remove(email)


def test_signup_already_signed():
    # john@mergington.edu is already signed up in many activities
    resp = client.post("/activities/Art Club/signup", params={"email": "john@mergington.edu"})
    assert resp.status_code == 400


def test_signup_activity_not_found():
    resp = client.post("/activities/Nonexistent/signup", params={"email": "a@b.com"})
    assert resp.status_code == 404

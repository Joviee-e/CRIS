# tests/test_workflow.py
import pytest

from app.models import User, Application, ActionLog
from app.extensions import db as _db


def create_admin_and_token(client):
    """
    Helper used by other tests:
    - register a user
    - promote to admin
    - login and return JWT access token
    """
    client.post(
        "/api/auth/register",
        json={"email": "admin@example.com", "password": "admin123"},
    )

    user = User.query.filter_by(email="admin@example.com").first()
    if not user:
        user = User(email="admin@example.com")
        user.set_password("admin123")
        _db.session.add(user)

    user.role = "admin"
    _db.session.commit()

    res = client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "admin123"},
    )
    assert res.status_code == 200, "login failed in test helper"
    token = res.get_json()["access"]
    return token


def _auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def _create_sample_application(client, token):
    payload = {
        "sr_no": 1,
        "purpose": "Test purpose",
        "department": "IT",
        "emp_no": "E001",
        "emp_name": "Test User",
        "designation": "Engineer",
        "remarks": "Test remarks",
    }
    res = client.post(
        "/api/applications/",
        json=payload,
        headers=_auth_header(token),
    )
    assert res.status_code == 201
    data = res.get_json()
    assert data["status"] == "submitted"
    return data["id"]


def test_invalid_transitions(client):
    """
    - cannot approve directly from submitted
    - cannot verify once already verified
    """
    token = create_admin_and_token(client)
    app_id = _create_sample_application(client, token)

    # try to approve directly from "submitted" -> should fail
    res = client.patch(
        f"/api/applications/{app_id}/approve",
        headers=_auth_header(token),
    )
    assert res.status_code == 400
    body = res.get_json()
    assert body["msg"] == "invalid transition"

    # valid verify
    res = client.patch(
        f"/api/applications/{app_id}/verify",
        headers=_auth_header(token),
    )
    assert res.status_code == 200

    # try to verify again -> invalid
    res = client.patch(
        f"/api/applications/{app_id}/verify",
        headers=_auth_header(token),
    )
    assert res.status_code == 400
    body = res.get_json()
    assert body["msg"] == "invalid transition"

    # now approve from verified -> should pass
    res = client.patch(
        f"/api/applications/{app_id}/approve",
        headers=_auth_header(token),
    )
    assert res.status_code == 200


def test_logs_created_and_retrievable(client):
    """
    Ensure we get logs for created -> verified -> approved.
    """
    token = create_admin_and_token(client)
    app_id = _create_sample_application(client, token)

    # verify with a note
    client.patch(
        f"/api/applications/{app_id}/verify",
        json={"note": "checked"},
        headers=_auth_header(token),
    )

    # approve with a note
    client.patch(
        f"/api/applications/{app_id}/approve",
        json={"note": "final ok"},
        headers=_auth_header(token),
    )

    # fetch logs via API
    res = client.get(
        f"/api/applications/{app_id}/logs",
        headers=_auth_header(token),
    )
    assert res.status_code == 200
    data = res.get_json()
    logs = data["logs"]
    # should at least have created, verified, approved
    actions = [log["action"] for log in logs]
    assert "created" in actions
    assert "verified" in actions
    assert "approved" in actions

    # each log should have actor and timestamp
    for log in logs:
        assert "actor_id" in log
        assert "created_at" in log

# tests/test_refresh_and_admin.py
import pytest
from app.models import User
from app.extensions import db

def login_and_get_tokens(client, email, password):
    rv = client.post("/api/auth/login", json={"email": email, "password": password})
    assert rv.status_code == 200
    data = rv.get_json()
    return data["access_token"], data["refresh_token"]

def test_refresh_returns_access(client):
    # Register & login
    client.post("/api/auth/register", json={"email": "ruser@example.com", "password": "pass"})
    _, refresh = login_and_get_tokens(client, "ruser@example.com", "pass")

    # call refresh endpoint with Authorization: Bearer <refresh>
    rv = client.post("/api/auth/refresh", headers={"Authorization": f"Bearer {refresh}"})
    assert rv.status_code == 200
    data = rv.get_json()
    assert "access_token" in data

def test_admin_promote_and_demote(client, db):
    # create admin and user
    client.post("/api/auth/register", json={"email": "adm@example.com", "password": "apass"})
    client.post("/api/auth/register", json={"email": "target@example.com", "password": "tpass"})
    # promote adm@example.com to admin directly in DB for test
    admin = User.query.filter_by(email="adm@example.com").first()
    admin.role = "admin"
    db.session.commit()

    # login admin and target
    access_admin, _ = login_and_get_tokens(client, "adm@example.com", "apass")
    target = User.query.filter_by(email="target@example.com").first()
    headers = {"Authorization": f"Bearer {access_admin}"}

    # promote target to manager
    rv = client.post("/api/admin/promote", json={"user_id": target.id, "role": "manager"}, headers=headers)
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["new_role"] == "manager"

    # demote back to user
    rv2 = client.post("/api/admin/demote", json={"user_id": target.id, "role": "user"}, headers=headers)
    assert rv2.status_code == 200
    data2 = rv2.get_json()
    assert data2["new_role"] == "user"

def test_non_admin_cannot_promote(client):
    # create regular user and login
    client.post("/api/auth/register", json={"email": "nadmin@example.com", "password": "np"})
    client.post("/api/auth/register", json={"email": "victim@example.com", "password": "v"})
    access_nonadmin, _ = login_and_get_tokens(client, "nadmin@example.com", "np")
    victim = User.query.filter_by(email="victim@example.com").first()
    headers = {"Authorization": f"Bearer {access_nonadmin}"}

    rv = client.post("/api/admin/promote", json={"user_id": victim.id, "role": "manager"}, headers=headers)
    assert rv.status_code == 403

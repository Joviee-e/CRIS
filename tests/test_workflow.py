# tests/test_workflow.py (replace or ensure this helper exists exactly)
from app.models import User
from app.extensions import db as _db

def create_admin_and_token(client):
    # register user
    client.post("/api/auth/register", json={"email":"admin@example.com","password":"admin123"})

    # ensure the DB user exists and promote to admin BEFORE login
    user = User.query.filter_by(email="admin@example.com").first()
    if not user:
        # defensive: if registration didn't create for some reason, create directly
        user = User(email="admin@example.com")
        user.set_password("admin123")
        _db.session.add(user)
    user.role = "admin"
    _db.session.commit()   # IMPORTANT: commit promotion before login

    # now login and obtain token that either has role claim or fallback will find admin role in DB
    res = client.post("/api/auth/login", json={"email":"admin@example.com","password":"admin123"})
    assert res.status_code == 200, "login failed in test helper"
    token = res.get_json()["access"]
    return token

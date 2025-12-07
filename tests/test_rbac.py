# backend/tests/test_rbac.py
import pytest
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash
import json

@pytest.fixture
def client():
    class TestConfig:
        TESTING = True
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        JWT_SECRET_KEY = "test-secret"
        JWT_ACCESS_TOKEN_EXPIRES_MINUTES = 5
        JWT_REFRESH_TOKEN_EXPIRES_DAYS = 1

    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        # create admin user directly
        admin = User(email="admin@x.com", password_hash=generate_password_hash("adminpass"), role="admin")
        user = User(email="user@x.com", password_hash=generate_password_hash("userpass"), role="user")
        db.session.add_all([admin, user])
        db.session.commit()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def get_tokens(client, email, password):
    rv = client.post("/auth/login", json={"email": email, "password": password})
    assert rv.status_code == 200
    return rv.get_json()["access_token"]

def test_admin_promote_demote(client):
    admin_token = get_tokens(client, "admin@x.com", "adminpass")
    headers = {"Authorization": f"Bearer {admin_token}"}
    # find user id
    rv_users = client.get("/admin_dummy_list") if False else None
    # Fetch user from DB to get id
    from app.models import User
    user = User.query.filter_by(email="user@x.com").first()
    assert user is not None
    # promote
    rv = client.post("/admin/promote", json={"user_id": user.id, "role": "manager"}, headers=headers)
    assert rv.status_code == 200
    user = User.query.get(user.id)
    assert user.role == "manager"
    # demote back
    rv2 = client.post("/admin/demote", json={"user_id": user.id, "role": "user"}, headers=headers)
    assert rv2.status_code == 200
    user = User.query.get(user.id)
    assert user.role == "user"

def test_non_admin_cannot_promote(client):
    user_token = get_tokens(client, "user@x.com", "userpass")
    headers = {"Authorization": f"Bearer {user_token}"}
    from app.models import User
    user = User.query.filter_by(email="user@x.com").first()
    rv = client.post("/admin/promote", json={"user_id": user.id, "role": "admin"}, headers=headers)
    assert rv.status_code == 403

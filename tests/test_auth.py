# backend/tests/test_auth.py
import json
import pytest
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

@pytest.fixture
def client(tmp_path, monkeypatch):
    # minimal test config
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
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def test_register_and_login_success(client):
    # register
    rv = client.post("/auth/register", json={"email": "user@example.com", "password": "pass123"})
    assert rv.status_code == 201
    data = rv.get_json()
    assert "access_token" in data and "refresh_token" in data
    # login
    rv2 = client.post("/auth/login", json={"email": "user@example.com", "password": "pass123"})
    assert rv2.status_code == 200
    data2 = rv2.get_json()
    assert "access_token" in data2

def test_register_duplicate(client):
    client.post("/auth/register", json={"email": "a@b.com", "password": "x"})
    rv = client.post("/auth/register", json={"email": "a@b.com", "password": "x"})
    assert rv.status_code == 409

def test_login_invalid(client):
    rv = client.post("/auth/login", json={"email": "noone@x.com", "password": "x"})
    assert rv.status_code == 401

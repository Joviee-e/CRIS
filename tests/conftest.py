# tests/conftest.py
import sys
import pathlib
import pytest

# Ensure project root is on sys.path so tests can import `app`
project_root = pathlib.Path(__file__).resolve().parents[1]  # backend/
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app import create_app
from app.extensions import db as _db

TEST_DB = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def app():
    config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": TEST_DB,
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "JWT_SECRET_KEY": "test-secret",
        "CORS_ORIGINS": "http://localhost:3000"
    }
    app = create_app()
    app.config.update(config)

    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()

@pytest.fixture(scope="session")
def client(app):
    return app.test_client()

@pytest.fixture(scope="session")
def db(app):
    # create all tables for tests
    _db.create_all()
    yield _db
    _db.session.remove()
    _db.drop_all()

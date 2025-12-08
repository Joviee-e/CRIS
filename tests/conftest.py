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
    # create app then apply test config (matches how some tests use the factory)
    app = create_app()
    app.config.update(config)

    # push app context for session lifetime
    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()

@pytest.fixture(scope="session")
def client(app):
    """
    Return a test client. Ensure DB tables exist for tests that use only `client`
    and do not directly request the `db` fixture.
    """
    # make sure tables exist (safe no-op if already created)
    _db.create_all()
    return app.test_client()

@pytest.fixture(scope="session")
def db(app):
    # create all tables for tests that explicitly depend on db fixture
    _db.create_all()
    yield _db
    _db.session.remove()
    _db.drop_all()

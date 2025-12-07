# app/auth/config.py
"""Compatibility shim for auth package."""

try:
    from app.config import Config  # type: ignore
except Exception:
    class Config:
        TESTING = True
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        JWT_SECRET_KEY = "test-secret"
        JWT_ACCESS_TOKEN_EXPIRES_MINUTES = 15
        JWT_REFRESH_TOKEN_EXPIRES_DAYS = 7

DEFAULT_ROLE = "user"
ACCESS_TOKEN_EXPIRES_MINUTES = 15
REFRESH_TOKEN_EXPIRES_DAYS = 7

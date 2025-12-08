import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret")

    # SQLITE for dev, ORACLE for staging/prod
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///dev.db")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = SECRET_KEY

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 5,
        "max_overflow": 10,
        "pool_pre_ping": True
    }

    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    RATELIMIT_STORAGE_URI = "memory://"   # explicit - ok for dev only
    # JWT defaults
    JWT_ACCESS_TOKEN_EXPIRES_MINUTES = 15
    JWT_REFRESH_TOKEN_EXPIRES_DAYS = 7

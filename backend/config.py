import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret-change-me")

    # JWT lives in localStorage on the frontend; 7-day expiry per TASK.md
    # so users don't need to log in again within the window.
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        days=int(os.getenv("JWT_ACCESS_DAYS", "7"))
    )

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URI", f"sqlite:///{BASE_DIR / 'trekking.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.getenv("SQL_ECHO", "0") == "1"

    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@trekking.org")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "AdminSecurePassword123!")

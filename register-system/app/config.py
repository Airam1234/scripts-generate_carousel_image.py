"""Application configuration, driven by environment variables.

Every setting has a safe default for local use. In production set
APP_ENV=production, SECRET_KEY and DATABASE_URL at minimum (see README).
"""
import os
from datetime import timedelta


def _bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _database_url():
    url = os.environ.get("DATABASE_URL", "sqlite:///register.db")
    # Many cloud hosts hand out postgres:// URLs; SQLAlchemy needs the driver name.
    if url.startswith("postgres://"):
        url = "postgresql+psycopg://" + url[len("postgres://"):]
    elif url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


class Config:
    APP_ENV = os.environ.get("APP_ENV", "development")
    ORGANISATION_NAME = os.environ.get("ORGANISATION_NAME", "Training Provider")
    SECRET_KEY = os.environ.get("SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    # Public address of the app, used to build links in pastoral emails.
    BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000").rstrip("/")
    TIMEZONE = os.environ.get("TIMEZONE", "Europe/London")

    # Sessions / cookies
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = _bool("SESSION_COOKIE_SECURE", APP_ENV == "production")
    PERMANENT_SESSION_LIFETIME = timedelta(
        minutes=int(os.environ.get("IDLE_TIMEOUT_MINUTES", "30"))
    )
    SESSION_REFRESH_EACH_REQUEST = True
    WTF_CSRF_TIME_LIMIT = None  # token lives as long as the login session
    TRUST_PROXY = _bool("TRUST_PROXY", False)

    # Login security
    MAX_FAILED_LOGINS = int(os.environ.get("MAX_FAILED_LOGINS", "5"))
    LOCKOUT_MINUTES = int(os.environ.get("LOCKOUT_MINUTES", "15"))
    MIN_PASSWORD_LENGTH = int(os.environ.get("MIN_PASSWORD_LENGTH", "12"))

    # Register rules
    PASTORAL_GRACE_MINUTES = int(os.environ.get("PASTORAL_GRACE_MINUTES", "15"))
    REGISTER_OPENS_MINUTES_BEFORE = int(os.environ.get("REGISTER_OPENS_MINUTES_BEFORE", "30"))
    TUTOR_EDIT_WINDOW_DAYS = int(os.environ.get("TUTOR_EDIT_WINDOW_DAYS", "7"))
    ATTENDANCE_THRESHOLD = float(os.environ.get("ATTENDANCE_THRESHOLD", "90"))

    # Background job that raises pastoral alerts 15 minutes after each session starts.
    ENABLE_SCHEDULER = _bool("ENABLE_SCHEDULER", True)
    SCHEDULER_INTERVAL_SECONDS = int(os.environ.get("SCHEDULER_INTERVAL_SECONDS", "60"))

    # Email (e.g. Microsoft 365: smtp.office365.com, port 587, STARTTLS)
    SMTP_HOST = os.environ.get("SMTP_HOST")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USERNAME = os.environ.get("SMTP_USERNAME")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
    SMTP_USE_TLS = _bool("SMTP_USE_TLS", True)
    MAIL_FROM = os.environ.get("MAIL_FROM", "registers@example.org")
    # Shared pastoral mailbox. If unset, every active Pastoral user is emailed.
    PASTORAL_EMAIL = os.environ.get("PASTORAL_EMAIL")

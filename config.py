"""
Expert Panel Recommendation System
====================================
Configuration module — reads from .env or environment variables.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Core Flask
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-please-change")
    FLASK_ENV: str = os.getenv("FLASK_ENV", "development")
    BASE_URL: str = os.getenv("BASE_URL", "")

    # Database
    SQLALCHEMY_DATABASE_URI: str = os.getenv("DATABASE_URL", "sqlite:///expert_panel.db")
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # Email
    MAIL_SERVER: str = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS: bool = os.getenv("MAIL_USE_TLS", "True") == "True"
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER: str = os.getenv("MAIL_DEFAULT_SENDER", "noreply@college.edu")

    # Admin defaults (used only on first run)
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@college.edu")

    # Institution
    COLLEGE_NAME: str = os.getenv("COLLEGE_NAME", "Expert College")

    # Panel composition
    INTERNAL_FACULTY_COUNT: int = 4
    EXTERNAL_FACULTY_COUNT: int = 3
    MAX_COURSES_PER_FACULTY: int = 2

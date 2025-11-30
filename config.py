import os
from datetime import timedelta


class Config:
    # Security
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"

    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)

    # Other settings
    UPLOAD_FOLDER = "uploads"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

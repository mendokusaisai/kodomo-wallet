"""
Configuration settings for the application.
"""

import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings"""

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]


settings = Settings()

"""
Configuration settings for the application.

Refactored to follow Interface Segregation Principle (ISP).
Each settings class has a single, focused responsibility.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class DatabaseSettings:
    """Database configuration - only database-related settings"""

    database_url: str

    @classmethod
    def from_env(cls) -> DatabaseSettings:
        """Load database settings from environment variables"""
        url = os.getenv("DATABASE_URL", "")
        return cls(database_url=url)


@dataclass(frozen=True)
class CORSSettings:
    """CORS configuration - only CORS-related settings"""

    cors_origins: list[str]

    @classmethod
    def from_env(cls) -> CORSSettings:
        """Load CORS settings from environment variables"""
        # Could be made configurable via env var if needed
        origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
        return cls(cors_origins=origins)


@dataclass(frozen=True)
class SecuritySettings:
    """Security configuration - only security-related settings"""

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    @classmethod
    def from_env(cls) -> SecuritySettings:
        """Load security settings from environment variables"""
        secret = os.getenv("SECRET_KEY", "")
        algorithm = os.getenv("ALGORITHM", "HS256")
        expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        return cls(
            secret_key=secret,
            algorithm=algorithm,
            access_token_expire_minutes=expire_minutes,
        )


@dataclass(frozen=True)
class SupabaseSettings:
    """Supabase configuration - only Supabase-related settings"""

    supabase_url: str
    supabase_key: str

    @classmethod
    def from_env(cls) -> SupabaseSettings:
        """Load Supabase settings from environment variables"""
        url = os.getenv("SUPABASE_URL", "")
        key = os.getenv("SUPABASE_KEY", "")
        return cls(supabase_url=url, supabase_key=key)


@dataclass(frozen=True)
class AppSettings:
    """Application general settings - environment and app-level config"""

    environment: str

    @classmethod
    def from_env(cls) -> AppSettings:
        """Load app settings from environment variables"""
        env = os.getenv("ENVIRONMENT", "development")
        return cls(environment=env)


# Singleton instances - loaded once at module import
database_settings = DatabaseSettings.from_env()
cors_settings = CORSSettings.from_env()
security_settings = SecuritySettings.from_env()
supabase_settings = SupabaseSettings.from_env()
app_settings = AppSettings.from_env()


# Backward compatibility facade - for gradual migration
class Settings:
    """
    Backward compatibility facade.

    This class provides the same interface as the old monolithic Settings class,
    but delegates to the new ISP-compliant setting classes.

    Usage: Prefer using specific settings classes (database_settings, cors_settings, etc.)
    """

    @property
    def DATABASE_URL(self) -> str:
        return database_settings.database_url

    @property
    def SUPABASE_URL(self) -> str:
        return supabase_settings.supabase_url

    @property
    def SUPABASE_KEY(self) -> str:
        return supabase_settings.supabase_key

    @property
    def SECRET_KEY(self) -> str:
        return security_settings.secret_key

    @property
    def ALGORITHM(self) -> str:
        return security_settings.algorithm

    @property
    def ACCESS_TOKEN_EXPIRE_MINUTES(self) -> int:
        return security_settings.access_token_expire_minutes

    @property
    def ENVIRONMENT(self) -> str:
        return app_settings.environment

    @property
    def CORS_ORIGINS(self) -> list[str]:
        return cors_settings.cors_origins


settings = Settings()

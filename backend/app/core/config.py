"""
アプリケーション設定

インターフェース分離の原則（ISP）に従ってリファクタリングされています。
各設定クラスは単一の明確な責任を持ちます。
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class DatabaseSettings:
    """データベース設定 - データベース関連の設定のみ"""

    database_url: str

    @classmethod
    def from_env(cls) -> DatabaseSettings:
        """環境変数からデータベース設定を読み込む"""
        url = os.getenv("DATABASE_URL", "")
        return cls(database_url=url)


@dataclass(frozen=True)
class CORSSettings:
    """CORS設定 - CORS関連の設定のみ"""

    cors_origins: list[str]

    @classmethod
    def from_env(cls) -> CORSSettings:
        """環境変数からCORS設定を読み込む"""
        # 必要に応じて環境変数で設定可能
        origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
        return cls(cors_origins=origins)


@dataclass(frozen=True)
class SecuritySettings:
    """セキュリティ設定 - セキュリティ関連の設定のみ"""

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    @classmethod
    def from_env(cls) -> SecuritySettings:
        """環境変数からセキュリティ設定を読み込む"""
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
    """Supabase設定 - Supabase関連の設定のみ"""

    supabase_url: str
    supabase_key: str

    @classmethod
    def from_env(cls) -> SupabaseSettings:
        """環境変数からSupabase設定を読み込む"""
        url = os.getenv("SUPABASE_URL", "")
        key = os.getenv("SUPABASE_KEY", "")
        return cls(supabase_url=url, supabase_key=key)


@dataclass(frozen=True)
class AppSettings:
    """アプリケーション全般設定 - 環境とアプリレベルの設定"""

    environment: str

    @classmethod
    def from_env(cls) -> AppSettings:
        """環境変数からアプリ設定を読み込む"""
        env = os.getenv("ENVIRONMENT", "development")
        return cls(environment=env)


# シングルトンインスタンス - モジュールインポート時に1度だけ読み込まれる
database_settings = DatabaseSettings.from_env()
cors_settings = CORSSettings.from_env()
security_settings = SecuritySettings.from_env()
supabase_settings = SupabaseSettings.from_env()
app_settings = AppSettings.from_env()


# 後方互換性のためのファサード - 段階的な移行用
class Settings:
    """
    後方互換性のためのファサード

    このクラスは旧モノリシックなSettingsクラスと同じインターフェースを提供しつつ、
    新しいISP準拠の設定クラスに委譲します。

    使い方: 可能な限り個別の設定クラス（database_settings、cors_settingsなど）を使用してください
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

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
    cors_origin_regex: str | None

    @classmethod
    def from_env(cls) -> CORSSettings:
        """環境変数からCORS設定を読み込む"""
        # デフォルトのローカルオリジン
        origins: list[str] = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
        # 追加のオリジンを環境変数から受け取る（カンマ区切り）
        env_origins = os.getenv("CORS_ORIGINS")
        if env_origins:
            for o in env_origins.split(","):
                o2 = o.strip()
                if o2:
                    origins.append(o2)
        # フロントエンドの本番オリジンがあれば追加
        fe_origin = os.getenv("FRONTEND_ORIGIN")
        if fe_origin:
            fe_origin = fe_origin.strip()
            if fe_origin and fe_origin not in origins:
                origins.append(fe_origin)

        # 正規表現パターンを環境変数から読み込む（Vercel preview環境用）
        # デフォルト: kodomo-wallet で始まる Vercel ドメインとローカルホストを許可
        regex_pattern = os.getenv(
            "CORS_ORIGIN_REGEX",
            r"^https://kodomo-wallet.*\.vercel\.app$|^http://localhost:3000$"
        )

        return cls(cors_origins=origins, cors_origin_regex=regex_pattern)


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


@dataclass(frozen=True)
class FrontendSettings:
    """フロントエンド関連の設定"""

    origin: str

    @classmethod
    def from_env(cls) -> FrontendSettings:
        """環境変数からフロント設定を読み込む"""
        origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
        return cls(origin=origin)


# シングルトンインスタンス - モジュールインポート時に1度だけ読み込まれる
database_settings = DatabaseSettings.from_env()
cors_settings = CORSSettings.from_env()
security_settings = SecuritySettings.from_env()
supabase_settings = SupabaseSettings.from_env()
app_settings = AppSettings.from_env()
frontend_settings = FrontendSettings.from_env()


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

    @property
    def FRONTEND_ORIGIN(self) -> str:
        return frontend_settings.origin


settings = Settings()

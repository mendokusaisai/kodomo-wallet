"""
アプリケーション設定

インターフェース分離の原則（ISP）に従って設定クラスを分割しています。
各設定クラスは単一の明確な責任を持ちます。
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class FirebaseSettings:
    """Firebase 設定 - Firebase Admin SDK 関連の設定のみ"""

    project_id: str
    service_account_json: str

    @classmethod
    def from_env(cls) -> FirebaseSettings:
        """環境変数から Firebase 設定を読み込む"""
        project_id = os.getenv("FIREBASE_PROJECT_ID", "kodomo-wallet-dev")
        service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT", "")
        return cls(project_id=project_id, service_account_json=service_account_json)


@dataclass(frozen=True)
class CORSSettings:
    """CORS設定 - CORS関連の設定のみ"""

    cors_origins: list[str]

    @classmethod
    def from_env(cls) -> CORSSettings:
        """環境変数からCORS設定を読み込む"""
        origins: list[str] = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
        env_origins = os.getenv("CORS_ORIGINS")
        if env_origins:
            for o in env_origins.split(","):
                o2 = o.strip()
                if o2:
                    origins.append(o2)
        fe_origin = os.getenv("FRONTEND_ORIGIN")
        if fe_origin:
            fe_origin = fe_origin.strip()
            if fe_origin and fe_origin not in origins:
                origins.append(fe_origin)

        return cls(cors_origins=origins)


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


# シングルトンインスタンス
firebase_settings = FirebaseSettings.from_env()
cors_settings = CORSSettings.from_env()
app_settings = AppSettings.from_env()
frontend_settings = FrontendSettings.from_env()


"""
Firestore クライアントの初期化
"""

import json
import os

import firebase_admin
from firebase_admin import credentials, firestore

from app.core.config import firebase_settings

_app: firebase_admin.App | None = None


def _get_firebase_app() -> firebase_admin.App:
    """Firebase Admin SDK アプリを取得（シングルトン）"""
    global _app
    if _app is not None:
        return _app

    # Emulator 使用時は認証不要
    if os.getenv("FIRESTORE_EMULATOR_HOST"):
        _app = firebase_admin.initialize_app(
            options={"projectId": firebase_settings.project_id}
        )
        return _app

    # サービスアカウント JSON が環境変数に設定されている場合
    if firebase_settings.service_account_json:
        cred_dict = json.loads(firebase_settings.service_account_json)
        cred = credentials.Certificate(cred_dict)
        _app = firebase_admin.initialize_app(cred)
        return _app

    # デフォルト認証情報（Cloud Run 等の GCP 環境）
    _app = firebase_admin.initialize_app()
    return _app


def get_firestore_client() -> firestore.Client:
    """Firestore クライアントを取得する"""
    _get_firebase_app()
    return firestore.client()

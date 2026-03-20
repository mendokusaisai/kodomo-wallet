"""
Firestore リポジトリテスト共通 fixture

Firestore Emulator への接続を設定します。
テスト実行前に FIRESTORE_EMULATOR_HOST 環境変数が設定されている必要があります。

  FIRESTORE_EMULATOR_HOST=localhost:8080 uv run pytest tests/repositories/
"""

import os

import pytest

# Emulator が起動していない場合はリポジトリテストをスキップ
if not os.getenv("FIRESTORE_EMULATOR_HOST"):
    pytest.skip(
        "FIRESTORE_EMULATOR_HOST is not set. Start Firebase Emulator first.",
        allow_module_level=True,
    )

import firebase_admin
from firebase_admin import credentials

from app.core.config import firebase_settings

# テスト用 Firebase アプリを初期化（未初期化の場合のみ）
if not firebase_admin._apps:
    firebase_admin.initialize_app(
        options={"projectId": firebase_settings.project_id}
    )

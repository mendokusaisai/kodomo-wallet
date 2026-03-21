"""
GraphQLコンテキスト管理

GraphQLリクエストのコンテキストを処理します。
Firebase Auth JWT 検証と Firestore ベースのサービスを提供します。
"""

from __future__ import annotations

import logging
from typing import Any

from firebase_admin import auth
from injector import Injector

from app.core.container import create_injector
from app.core.exceptions import ResourceNotFoundException
from app.services import AccountService, FamilyService, TransactionService

logger = logging.getLogger(__name__)


def verify_firebase_token(token: str) -> dict:
    """Firebase ID トークンを検証してデコード済みクレームを返す"""
    try:
        return auth.verify_id_token(token)
    except Exception as e:
        raise ResourceNotFoundException("FirebaseToken", str(e)) from e


class GraphQLContext:
    """GraphQLリクエスト用のコンテキスト"""

    def __init__(self) -> None:
        self._injector: Injector | None = None
        self.current_uid: str | None = None
        self.family_service: FamilyService | None = None
        self.account_service: AccountService | None = None
        self.transaction_service: TransactionService | None = None

    def __enter__(self) -> GraphQLContext:
        self._injector = create_injector()
        self.family_service = self._injector.get(FamilyService)
        self.account_service = self._injector.get(AccountService)
        self.transaction_service = self._injector.get(TransactionService)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self._injector = None

    async def __aenter__(self) -> GraphQLContext:
        return self.__enter__()

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.__exit__(exc_type, exc_val, exc_tb)

    def to_dict(self) -> dict[str, Any]:
        return {
            "current_uid": self.current_uid,
            "family_service": self.family_service,
            "account_service": self.account_service,
            "transaction_service": self.transaction_service,
        }


"""
GraphQLコンテキスト管理

GraphQLリクエストのコンテキストを処理するコンテキストマネージャークラスを提供します。
データベースセッションのライフサイクルとサービスの注入を含みます。
"""

from __future__ import annotations

from typing import Any

from injector import Injector
from sqlalchemy.orm import Session

from app.core.container import create_injector
from app.core.database import SessionLocal
from app.services import (
    AccountService,
    ProfileService,
    RecurringDepositService,
    TransactionService,
    WithdrawalRequestService,
)


class GraphQLContext:
    """
    GraphQLリクエスト用のコンテキストマネージャー

    データベースセッションと注入されたサービスのライフサイクルを管理します。
    エラーが発生した場合でも適切なリソースのクリーンアップを保証します。

    Attributes:
        db: SQLAlchemyデータベースセッション
        profile_service: 注入されたProfileServiceインスタンス
        account_service: 注入されたAccountServiceインスタンス
        transaction_service: 注入されたTransactionServiceインスタンス
    """

    def __init__(self) -> None:
        """コンテキストを初期化（リソースはenter時に作成されます）"""
        self._db: Session | None = None
        self._injector: Injector | None = None
        self.profile_service: ProfileService | None = None
        self.account_service: AccountService | None = None
        self.transaction_service: TransactionService | None = None
        self.withdrawal_request_service: WithdrawalRequestService | None = None
        self.recurring_deposit_service: RecurringDepositService | None = None

    @property
    def db(self) -> Session:
        """データベースセッションを取得（初期化されていない場合はエラー）"""
        if self._db is None:
            raise RuntimeError("Database session not initialized. Use context manager.")
        return self._db

    def __enter__(self) -> GraphQLContext:
        """
        コンテキストマネージャーに入ります。

        データベースセッションを作成しサービスを初期化します。

        Returns:
            GraphQLContext: すべてのリソースが初期化されたコンテキスト
        """
        self._db = SessionLocal()
        self._injector = create_injector(self._db)

        # サービスを注入
        self.profile_service = self._injector.get(ProfileService)
        self.account_service = self._injector.get(AccountService)
        self.transaction_service = self._injector.get(TransactionService)
        self.withdrawal_request_service = self._injector.get(WithdrawalRequestService)
        self.recurring_deposit_service = self._injector.get(RecurringDepositService)

        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        コンテキストマネージャーを終了します。

        例外が発生していなければトランザクションをコミットし、
        例外が発生していればロールバックします。
        すべてのケースでデータベースセッションが適切にクローズされることを保証します。

        Args:
            exc_type: 例外の型（ある場合）
            exc_val: 例外の値（ある場合）
            exc_tb: 例外のトレースバック（ある場合）
        """
        if self._db is not None:
            try:
                if exc_type is None:
                    # 例外なし: トランザクションをコミット
                    self._db.commit()
                else:
                    # 例外発生: トランザクションをロールバック
                    self._db.rollback()
            finally:
                self._db.close()
                self._db = None
        self._injector = None
        self.profile_service = None
        self.account_service = None
        self.transaction_service = None
        self.withdrawal_request_service = None
        self.recurring_deposit_service = None

    async def __aenter__(self) -> GraphQLContext:
        """
        非同期コンテキストとの互換性のための非同期enter

        Returns:
            GraphQLContext: 初期化されたコンテキスト
        """
        return self.__enter__()

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        非同期コンテキストとの互換性のための非同期exit

        Args:
            exc_type: 例外の型（ある場合）
            exc_val: 例外の値（ある場合）
            exc_tb: 例外のトレースバック（ある場合）
        """
        self.__exit__(exc_type, exc_val, exc_tb)

    def to_dict(self) -> dict[str, Any]:
        """
        コンテキストをGraphQL用の辞書に変換します。

        Returns:
            dict: dbとサービスを含む辞書形式のコンテキスト
        """
        return {
            "db": self.db,
            "profile_service": self.profile_service,
            "account_service": self.account_service,
            "transaction_service": self.transaction_service,
            "withdrawal_request_service": self.withdrawal_request_service,
            "recurring_deposit_service": self.recurring_deposit_service,
        }

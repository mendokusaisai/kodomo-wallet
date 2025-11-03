"""
'injector'パッケージを使用した依存性注入コンテナ

以下の特徴を持つクリーンで保守性の高いDI実装を提供します:
- 自動的な依存性解決
- 型安全なバインディング
- スコープ管理（Singleton、リクエストスコープなど）
- Moduleのオーバーライドによる簡単なテスト
"""

from injector import Binder, Injector, Module, singleton
from sqlalchemy.orm import Session

from app.repositories.interfaces import (
    AccountRepository,
    FamilyRelationshipRepository,
    ParentInviteRepository,
    ProfileRepository,
    RecurringDepositExecutionRepository,
    RecurringDepositRepository,
    TransactionRepository,
    WithdrawalRequestRepository,
)
from app.repositories.sqlalchemy import (
    SQLAlchemyAccountRepository,
    SQLAlchemyFamilyRelationshipRepository,
    SQLAlchemyParentInviteRepository,
    SQLAlchemyProfileRepository,
    SQLAlchemyRecurringDepositExecutionRepository,
    SQLAlchemyRecurringDepositRepository,
    SQLAlchemyTransactionRepository,
    SQLAlchemyWithdrawalRequestRepository,
)
from app.services.mailer import ConsoleMailer, Mailer


class RepositoryModule(Module):
    """
    Repositoryのバインディングを設定するモジュール

    このモジュールはRepositoryインターフェースをSQLAlchemy実装にバインドします。
    """

    def __init__(self, db: Session):
        self.db = db

    def configure(self, binder: Binder) -> None:
        """Repositoryのバインディングを設定"""
        # RepositoryインターフェースをSQLAlchemy実装にバインド
        # 各リポジトリは同じデータベースセッションを使用
        binder.bind(
            ProfileRepository,
            to=SQLAlchemyProfileRepository(self.db),
            scope=singleton,
        )
        binder.bind(
            AccountRepository,
            to=SQLAlchemyAccountRepository(self.db),
            scope=singleton,
        )
        binder.bind(
            TransactionRepository,
            to=SQLAlchemyTransactionRepository(self.db),
            scope=singleton,
        )
        binder.bind(
            WithdrawalRequestRepository,
            to=SQLAlchemyWithdrawalRequestRepository(self.db),
            scope=singleton,
        )
        binder.bind(
            RecurringDepositRepository,
            to=SQLAlchemyRecurringDepositRepository(self.db),
            scope=singleton,
        )
        binder.bind(
            RecurringDepositExecutionRepository,
            to=SQLAlchemyRecurringDepositExecutionRepository(self.db),
            scope=singleton,
        )
        binder.bind(
            FamilyRelationshipRepository,
            to=SQLAlchemyFamilyRelationshipRepository(self.db),
            scope=singleton,
        )
        binder.bind(
            ParentInviteRepository,
            to=SQLAlchemyParentInviteRepository(self.db),
            scope=singleton,
        )

        # Mailer（スタブ実装）
        binder.bind(
            Mailer,
            to=ConsoleMailer(),
            scope=singleton,
        )


def create_injector(db: Session) -> Injector:
    """
    設定済みのInjectorインスタンスを作成します。

    Args:
        db: SQLAlchemyデータベースセッション

    Returns:
        設定済みのInjectorインスタンス

    Example:
        >>> from app.core.database import get_db
        >>> db = next(get_db())
        >>> injector = create_injector(db)
        >>> profile_service = injector.get(ProfileService)
    """
    return Injector([RepositoryModule(db)])

"""
AccountRepositoryのSQLAlchemy実装
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.domain.entities import Account
from app.repositories.interfaces import AccountRepository
from app.repositories.sqlalchemy import models as db_models
from app.repositories.sqlalchemy.mapper import to_domain_account


class SQLAlchemyAccountRepository(AccountRepository):
    """AccountRepositoryのSQLAlchemy実装"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: str) -> list[Account]:
        """ユーザーの全アカウントを取得"""
        db_accounts = (
            self.db.query(db_models.Account)
            .filter(db_models.Account.user_id == uuid.UUID(user_id))
            .all()
        )
        return [to_domain_account(acc) for acc in db_accounts]

    def get_by_id(self, account_id: str) -> Account | None:
        """IDでアカウントを取得"""
        db_account = (
            self.db.query(db_models.Account)
            .filter(db_models.Account.id == uuid.UUID(account_id))
            .first()
        )
        return to_domain_account(db_account) if db_account else None

    def update_balance(self, account: Account, new_balance: int) -> None:
        """アカウント残高を更新"""
        db_account = (
            self.db.query(db_models.Account)
            .filter(db_models.Account.id == uuid.UUID(account.id))
            .first()
        )
        if db_account:
            db_account.balance = new_balance  # type: ignore
            db_account.updated_at = str(datetime.now(UTC))  # type: ignore
            self.db.flush()

    def update(self, account: Account) -> Account:
        """アカウントを更新"""
        db_account = (
            self.db.query(db_models.Account)
            .filter(db_models.Account.id == uuid.UUID(account.id))
            .first()
        )
        if not db_account:
            raise ValueError(f"Account {account.id} not found")

        # ドメインエンティティの値でDBモデルを更新
        db_account.balance = account.balance  # type: ignore
        db_account.currency = account.currency  # type: ignore
        db_account.goal_name = account.goal_name  # type: ignore
        db_account.goal_amount = account.goal_amount  # type: ignore
        db_account.updated_at = str(account.updated_at)  # type: ignore
        self.db.flush()
        self.db.refresh(db_account)
        return to_domain_account(db_account)

    def create(self, user_id: str, balance: int, currency: str) -> Account:
        """新規アカウントを作成"""
        db_account = db_models.Account(
            id=uuid.uuid4(),
            user_id=uuid.UUID(user_id),
            balance=balance,
            currency=currency,
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        self.db.add(db_account)
        self.db.flush()
        self.db.refresh(db_account)
        return to_domain_account(db_account)

    def delete(self, account_id: str) -> bool:
        """アカウントを削除"""
        db_account = (
            self.db.query(db_models.Account)
            .filter(db_models.Account.id == uuid.UUID(account_id))
            .first()
        )
        if not db_account:
            return False
        self.db.delete(db_account)
        self.db.flush()
        return True

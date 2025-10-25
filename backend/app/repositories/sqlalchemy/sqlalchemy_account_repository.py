"""
AccountRepositoryのSQLAlchemy実装
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.models import Account
from app.repositories.interfaces import AccountRepository


class SQLAlchemyAccountRepository(AccountRepository):
    """AccountRepositoryのSQLAlchemy実装"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: str) -> list[Account]:
        """ユーザーの全アカウントを取得"""
        return list(self.db.query(Account).filter(Account.user_id == uuid.UUID(user_id)).all())

    def get_by_id(self, account_id: str) -> Account | None:
        """IDでアカウントを取得"""
        return self.db.query(Account).filter(Account.id == uuid.UUID(account_id)).first()

    def update_balance(self, account: Account, new_balance: int) -> None:
        """アカウント残高を更新"""
        account.balance = new_balance
        self.db.flush()

    def create(self, user_id: str, balance: int, currency: str) -> Account:
        """新規アカウントを作成"""
        account = Account(
            id=uuid.uuid4(),
            user_id=uuid.UUID(user_id),
            balance=balance,
            currency=currency,
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        self.db.add(account)
        self.db.flush()
        return account

    def delete(self, account_id: str) -> bool:
        """アカウントを削除"""
        account = self.get_by_id(account_id)
        if not account:
            return False
        self.db.delete(account)
        self.db.flush()
        return True

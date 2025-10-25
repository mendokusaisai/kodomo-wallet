"""
TransactionRepositoryのSQLAlchemy実装
"""

import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.models import Transaction
from app.repositories.interfaces import TransactionRepository


class SQLAlchemyTransactionRepository(TransactionRepository):
    """TransactionRepositoryのSQLAlchemy実装"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_account_id(self, account_id: str, limit: int = 50) -> list[Transaction]:
        """アカウントのトランザクションを取得"""
        return list(
            self.db.query(Transaction)
            .filter(Transaction.account_id == uuid.UUID(account_id))
            .order_by(Transaction.created_at.desc())
            .limit(limit)
            .all()
        )

    def create(
        self,
        account_id: str,
        transaction_type: str,
        amount: int,
        description: str | None,
        created_at: datetime,
    ) -> Transaction:
        """新規トランザクションを作成"""
        transaction = Transaction(
            account_id=uuid.UUID(account_id),
            type=transaction_type,
            amount=amount,
            description=description,
            created_at=str(created_at),
        )
        self.db.add(transaction)
        self.db.flush()
        self.db.refresh(transaction)
        return transaction

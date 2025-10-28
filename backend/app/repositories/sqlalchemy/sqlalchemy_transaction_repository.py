"""
TransactionRepositoryのSQLAlchemy実装
"""

import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.domain.entities import Transaction
from app.repositories.interfaces import TransactionRepository
from app.repositories.sqlalchemy import models as db_models
from app.repositories.sqlalchemy.mapper import to_domain_transaction


class SQLAlchemyTransactionRepository(TransactionRepository):
    """TransactionRepositoryのSQLAlchemy実装"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_account_id(self, account_id: str, limit: int = 50) -> list[Transaction]:
        """アカウントのトランザクションを取得"""
        db_transactions = (
            self.db.query(db_models.Transaction)
            .filter(db_models.Transaction.account_id == uuid.UUID(account_id))
            .order_by(db_models.Transaction.created_at.desc())
            .limit(limit)
            .all()
        )
        return [to_domain_transaction(t) for t in db_transactions]

    def create(
        self,
        account_id: str,
        transaction_type: str,
        amount: int,
        description: str | None,
        created_at: datetime,
    ) -> Transaction:
        """新規トランザクションを作成"""
        db_transaction = db_models.Transaction(
            account_id=uuid.UUID(account_id),
            type=transaction_type,
            amount=amount,
            description=description,
            created_at=str(created_at),
        )
        self.db.add(db_transaction)
        self.db.flush()
        self.db.refresh(db_transaction)
        return to_domain_transaction(db_transaction)

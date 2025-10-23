"""
SQLAlchemy implementation of repository interfaces.
"""

import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.models import Account, Profile, Transaction
from app.repositories.interfaces import (
    AccountRepository,
    ProfileRepository,
    TransactionRepository,
)


class SQLAlchemyProfileRepository(ProfileRepository):
    """SQLAlchemy implementation of ProfileRepository"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: str) -> Profile | None:
        """Get profile by ID"""
        return self.db.query(Profile).filter(Profile.id == uuid.UUID(user_id)).first()


class SQLAlchemyAccountRepository(AccountRepository):
    """SQLAlchemy implementation of AccountRepository"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: str) -> list[Account]:
        """Get all accounts for a user"""
        return list(self.db.query(Account).filter(Account.user_id == uuid.UUID(user_id)).all())

    def get_by_id(self, account_id: str) -> Account | None:
        """Get account by ID"""
        return self.db.query(Account).filter(Account.id == uuid.UUID(account_id)).first()

    def update_balance(self, account: Account, new_balance: int) -> None:
        """Update account balance"""
        account.balance = new_balance
        self.db.flush()


class SQLAlchemyTransactionRepository(TransactionRepository):
    """SQLAlchemy implementation of TransactionRepository"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_account_id(self, account_id: str, limit: int = 50) -> list[Transaction]:
        """Get transactions for an account"""
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
        """Create a new transaction"""
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

"""
SQLAlchemy implementation of repository interfaces.
"""

import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.models import Account, Profile, Transaction, WithdrawalRequest
from app.repositories.interfaces import (
    AccountRepository,
    ProfileRepository,
    TransactionRepository,
    WithdrawalRequestRepository,
)


class SQLAlchemyProfileRepository(ProfileRepository):
    """SQLAlchemy implementation of ProfileRepository"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: str) -> Profile | None:
        """Get profile by ID"""
        return self.db.query(Profile).filter(Profile.id == uuid.UUID(user_id)).first()

    def get_children(self, parent_id: str) -> list[Profile]:
        """Get all children profiles for a parent"""
        return list(
            self.db.query(Profile).filter(Profile.parent_id == uuid.UUID(parent_id)).all()
        )

    def get_by_auth_user_id(self, auth_user_id: str) -> Profile | None:
        """Get profile by auth user ID"""
        return (
            self.db.query(Profile)
            .filter(Profile.auth_user_id == uuid.UUID(auth_user_id))
            .first()
        )

    def get_by_email(self, email: str) -> Profile | None:
        """Get unauthenticated profile by email (auth_user_id is NULL)"""
        return (
            self.db.query(Profile)
            .filter(Profile.email == email)
            .filter(Profile.auth_user_id.is_(None))  # 未認証のみ
            .first()
        )

    def create_child(self, name: str, parent_id: str, email: str | None = None) -> Profile:
        """Create a child profile without authentication"""
        from datetime import UTC, datetime

        profile = Profile(
            id=uuid.uuid4(),
            auth_user_id=None,  # 認証なし
            email=email,  # メールアドレス（任意）
            name=name,
            role="child",
            parent_id=uuid.UUID(parent_id),
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        self.db.add(profile)
        self.db.flush()
        return profile

    def link_to_auth(self, profile_id: str, auth_user_id: str) -> Profile:
        """Link existing profile to auth account"""
        from datetime import UTC, datetime

        profile = self.get_by_id(profile_id)
        if not profile:
            raise ValueError(f"Profile {profile_id} not found")

        # 既に認証アカウントが紐づいている場合はエラー
        if profile.auth_user_id:
            raise ValueError(f"Profile {profile_id} already linked to auth account")

        profile.auth_user_id = uuid.UUID(auth_user_id)
        profile.updated_at = str(datetime.now(UTC))
        self.db.flush()
        return profile


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

    def create(self, user_id: str, balance: int, currency: str) -> Account:
        """Create a new account"""
        from datetime import UTC, datetime

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


class SQLAlchemyWithdrawalRequestRepository(WithdrawalRequestRepository):
    """SQLAlchemy implementation of WithdrawalRequestRepository"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, request_id: str) -> WithdrawalRequest | None:
        """Get withdrawal request by ID"""
        return (
            self.db.query(WithdrawalRequest)
            .filter(WithdrawalRequest.id == uuid.UUID(request_id))
            .first()
        )

    def get_pending_by_parent(self, parent_id: str) -> list[WithdrawalRequest]:
        """Get all pending withdrawal requests for a parent's children"""
        from app.models.models import Account, Profile

        return list(
            self.db.query(WithdrawalRequest)
            .join(Account, WithdrawalRequest.account_id == Account.id)
            .join(Profile, Account.user_id == Profile.id)
            .filter(Profile.parent_id == uuid.UUID(parent_id))
            .filter(WithdrawalRequest.status == "pending")
            .order_by(WithdrawalRequest.created_at.desc())
            .all()
        )

    def create(
        self,
        account_id: str,
        amount: int,
        description: str | None,
        created_at: datetime,
    ) -> WithdrawalRequest:
        """Create a new withdrawal request"""
        request = WithdrawalRequest(
            id=uuid.uuid4(),
            account_id=uuid.UUID(account_id),
            amount=amount,
            description=description,
            status="pending",
            created_at=str(created_at),
            updated_at=str(created_at),
        )
        self.db.add(request)
        self.db.flush()
        self.db.refresh(request)
        return request

    def update_status(
        self, request: WithdrawalRequest, status: str, updated_at: datetime
    ) -> WithdrawalRequest:
        """Update withdrawal request status"""
        request.status = status  # type: ignore
        request.updated_at = str(updated_at)  # type: ignore
        self.db.flush()
        self.db.refresh(request)
        return request

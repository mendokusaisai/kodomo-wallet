"""
Repository interfaces (Abstract Base Classes) for data access.
"""

from abc import ABC, abstractmethod
from datetime import datetime

from app.models.models import Account, Profile, Transaction


class ProfileRepository(ABC):
    """Interface for Profile data access"""

    @abstractmethod
    def get_by_id(self, user_id: str) -> Profile | None:
        """Get profile by ID"""
        pass


class AccountRepository(ABC):
    """Interface for Account data access"""

    @abstractmethod
    def get_by_user_id(self, user_id: str) -> list[Account]:
        """Get all accounts for a user"""
        pass

    @abstractmethod
    def get_by_id(self, account_id: str) -> Account | None:
        """Get account by ID"""
        pass

    @abstractmethod
    def update_balance(self, account: Account, new_balance: int) -> None:
        """Update account balance"""
        pass


class TransactionRepository(ABC):
    """Interface for Transaction data access"""

    @abstractmethod
    def get_by_account_id(self, account_id: str, limit: int = 50) -> list[Transaction]:
        """Get transactions for an account"""
        pass

    @abstractmethod
    def create(
        self,
        account_id: str,
        transaction_type: str,
        amount: int,
        description: str | None,
        created_at: datetime,
    ) -> Transaction:
        """Create a new transaction"""
        pass

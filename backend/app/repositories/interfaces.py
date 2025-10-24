"""
Repository interfaces (Abstract Base Classes) for data access.
"""

from abc import ABC, abstractmethod
from datetime import datetime

from app.models.models import Account, Profile, RecurringDeposit, Transaction, WithdrawalRequest


class ProfileRepository(ABC):
    """Interface for Profile data access"""

    @abstractmethod
    def get_by_id(self, user_id: str) -> Profile | None:
        """Get profile by ID"""
        pass

    @abstractmethod
    def get_children(self, parent_id: str) -> list[Profile]:
        """Get all children profiles for a parent"""
        pass

    @abstractmethod
    def get_by_auth_user_id(self, auth_user_id: str) -> Profile | None:
        """Get profile by auth user ID"""
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Profile | None:
        """Get unauthenticated profile by email (auth_user_id is NULL)"""
        pass

    @abstractmethod
    def create_child(self, name: str, parent_id: str, email: str | None = None) -> Profile:
        """Create a child profile without authentication"""
        pass

    @abstractmethod
    def link_to_auth(self, profile_id: str, auth_user_id: str) -> Profile:
        """Link existing profile to auth account"""
        pass

    @abstractmethod
    def delete(self, user_id: str) -> bool:
        """Delete a profile"""
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

    @abstractmethod
    def create(self, user_id: str, balance: int, currency: str) -> Account:
        """Create a new account"""
        pass

    @abstractmethod
    def delete(self, account_id: str) -> bool:
        """Delete an account"""
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


class WithdrawalRequestRepository(ABC):
    """Interface for WithdrawalRequest data access"""

    @abstractmethod
    def get_by_id(self, request_id: str) -> WithdrawalRequest | None:
        """Get withdrawal request by ID"""
        pass

    @abstractmethod
    def get_pending_by_parent(self, parent_id: str) -> list[WithdrawalRequest]:
        """Get all pending withdrawal requests for a parent's children"""
        pass

    @abstractmethod
    def create(
        self,
        account_id: str,
        amount: int,
        description: str | None,
        created_at: datetime,
    ) -> WithdrawalRequest:
        """Create a new withdrawal request"""
        pass

    @abstractmethod
    def update_status(
        self, request: WithdrawalRequest, status: str, updated_at: datetime
    ) -> WithdrawalRequest:
        """Update withdrawal request status"""
        pass


class RecurringDepositRepository(ABC):
    """Interface for RecurringDeposit data access"""

    @abstractmethod
    def get_by_account_id(self, account_id: str) -> RecurringDeposit | None:
        """Get recurring deposit settings by account ID"""
        pass

    @abstractmethod
    def create(
        self,
        account_id: str,
        amount: int,
        day_of_month: int,
        created_at: datetime,
    ) -> RecurringDeposit:
        """Create a new recurring deposit setting"""
        pass

    @abstractmethod
    def update(
        self,
        recurring_deposit: RecurringDeposit,
        amount: int | None,
        day_of_month: int | None,
        is_active: bool | None,
        updated_at: datetime,
    ) -> RecurringDeposit:
        """Update recurring deposit settings"""
        pass

    @abstractmethod
    def delete(self, recurring_deposit: RecurringDeposit) -> bool:
        """Delete recurring deposit settings"""
        pass

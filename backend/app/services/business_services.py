"""
Business logic services.

These services contain the business logic and use repositories for data access.
"""

from datetime import UTC, datetime

from injector import inject

from app.models.models import Account, Profile, Transaction
from app.repositories.interfaces import (
    AccountRepository,
    ProfileRepository,
    TransactionRepository,
)


class ProfileService:
    """Service for profile-related business logic"""

    @inject
    def __init__(self, profile_repo: ProfileRepository):
        self.profile_repo = profile_repo

    def get_profile(self, user_id: str) -> Profile | None:
        """Get user profile by ID"""
        return self.profile_repo.get_by_id(user_id)


class AccountService:
    """Service for account-related business logic"""

    @inject
    def __init__(self, account_repo: AccountRepository):
        self.account_repo = account_repo

    def get_user_accounts(self, user_id: str) -> list[Account]:
        """Get all accounts for a user"""
        return self.account_repo.get_by_user_id(user_id)


class TransactionService:
    """Service for transaction-related business logic"""

    @inject
    def __init__(
        self,
        transaction_repo: TransactionRepository,
        account_repo: AccountRepository,
    ):
        self.transaction_repo = transaction_repo
        self.account_repo = account_repo

    def get_account_transactions(self, account_id: str, limit: int = 50) -> list[Transaction]:
        """Get transactions for an account"""
        return self.transaction_repo.get_by_account_id(account_id, limit)

    def create_deposit(
        self, account_id: str, amount: int, description: str | None = None
    ) -> Transaction:
        """Create a deposit transaction and update account balance"""
        # Get account
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ValueError("Account not found")

        # Update balance
        new_balance = int(account.balance) + amount
        self.account_repo.update_balance(account, new_balance)

        # Create transaction
        transaction = self.transaction_repo.create(
            account_id=account_id,
            transaction_type="deposit",
            amount=amount,
            description=description,
            created_at=datetime.now(UTC),
        )

        return transaction

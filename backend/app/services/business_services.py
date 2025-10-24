"""
Business logic services.

These services contain the business logic and use repositories for data access.
"""

from datetime import UTC, datetime

from injector import inject

from app.core.exceptions import InvalidAmountException, ResourceNotFoundException
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

    def get_children(self, parent_id: str) -> list[Profile]:
        """Get all children for a parent"""
        return self.profile_repo.get_children(parent_id)


class AccountService:
    """Service for account-related business logic"""

    @inject
    def __init__(
        self, account_repo: AccountRepository, profile_repo: ProfileRepository
    ):
        self.account_repo = account_repo
        self.profile_repo = profile_repo

    def get_user_accounts(self, user_id: str) -> list[Account]:
        """Get all accounts for a user"""
        return self.account_repo.get_by_user_id(user_id)

    def get_family_accounts(self, user_id: str) -> list[Account]:
        """Get accounts for user. If parent, only return children's accounts"""
        # Get user profile to check role
        profile = self.profile_repo.get_by_id(user_id)

        if profile and profile.role == "parent":
            # Parents only see their children's accounts, not their own
            accounts = []
            children = self.profile_repo.get_children(user_id)
            for child in children:
                child_accounts = self.account_repo.get_by_user_id(str(child.id))
                accounts.extend(child_accounts)
        else:
            # Children see their own accounts
            accounts = self.account_repo.get_by_user_id(user_id)

        return accounts


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
        # Validate amount
        if amount <= 0:
            raise InvalidAmountException(amount, "Amount must be greater than zero")

        # Get account
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ResourceNotFoundException("Account", account_id)

        # Update balance (type: ignore for SQLAlchemy Column type)
        new_balance = int(account.balance) + amount  # type: ignore[arg-type]
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

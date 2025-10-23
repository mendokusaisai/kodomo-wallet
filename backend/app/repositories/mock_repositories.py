"""
Mock implementations of repositories for testing.
"""

from datetime import datetime

from app.models.models import Account, Profile, Transaction
from app.repositories.interfaces import (
    AccountRepository,
    ProfileRepository,
    TransactionRepository,
)


class MockProfileRepository(ProfileRepository):
    """Mock implementation of ProfileRepository for testing"""

    def __init__(self):
        self.profiles: dict[str, Profile] = {}

    def get_by_id(self, user_id: str) -> Profile | None:
        """Get profile by ID"""
        return self.profiles.get(user_id)

    def add(self, profile: Profile) -> None:
        """Add a profile for testing"""
        self.profiles[str(profile.id)] = profile


class MockAccountRepository(AccountRepository):
    """Mock implementation of AccountRepository for testing"""

    def __init__(self):
        self.accounts: dict[str, Account] = {}

    def get_by_user_id(self, user_id: str) -> list[Account]:
        """Get all accounts for a user"""
        return [acc for acc in self.accounts.values() if str(acc.user_id) == user_id]

    def get_by_id(self, account_id: str) -> Account | None:
        """Get account by ID"""
        return self.accounts.get(account_id)

    def update_balance(self, account: Account, new_balance: int) -> None:
        """Update account balance"""
        account.balance = new_balance

    def add(self, account: Account) -> None:
        """Add an account for testing"""
        self.accounts[str(account.id)] = account


class MockTransactionRepository(TransactionRepository):
    """Mock implementation of TransactionRepository for testing"""

    def __init__(self):
        self.transactions: list[Transaction] = []

    def get_by_account_id(self, account_id: str, limit: int = 50) -> list[Transaction]:
        """Get transactions for an account"""
        account_transactions = [t for t in self.transactions if str(t.account_id) == account_id]
        # Sort by created_at descending
        account_transactions.sort(key=lambda t: t.created_at, reverse=True)
        return account_transactions[:limit]

    def create(
        self,
        account_id: str,
        transaction_type: str,
        amount: int,
        description: str | None,
        created_at: datetime,
    ) -> Transaction:
        """Create a new transaction"""
        from uuid import UUID, uuid4

        transaction = Transaction(
            id=uuid4(),
            account_id=UUID(account_id),
            type=transaction_type,
            amount=amount,
            description=description,
            created_at=created_at,
        )
        self.transactions.append(transaction)
        return transaction

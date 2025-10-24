"""
GraphQL resolvers for queries and mutations.

These resolvers use Service layer dependencies without knowing about database details.
"""

from app.api.graphql.types import Account, Profile, Transaction
from app.services.business_services import (
    AccountService,
    ProfileService,
    TransactionService,
)


def get_profile_by_id(
    user_id: str,
    profile_service: ProfileService,
) -> Profile | None:
    """Get user profile by ID"""
    return profile_service.get_profile(user_id)


def get_accounts_by_user_id(
    user_id: str,
    account_service: AccountService,
    profile_service: ProfileService,
) -> list[Account]:
    """Get all accounts for a user and their children (if parent)"""
    accounts = account_service.get_family_accounts(user_id)

    # 各アカウントにユーザー情報を付与
    for account in accounts:
        user_profile = profile_service.get_profile(str(account.user_id))
        if user_profile:
            account.user = user_profile

    return accounts


def get_transactions_by_account_id(
    account_id: str,
    transaction_service: TransactionService,
    limit: int = 50,
) -> list[Transaction]:
    """Get transactions for an account"""
    return transaction_service.get_account_transactions(account_id, limit)


def create_deposit(
    account_id: str,
    amount: int,
    transaction_service: TransactionService,
    description: str | None = None,
) -> Transaction:
    """Create a deposit transaction"""
    return transaction_service.create_deposit(account_id, amount, description)

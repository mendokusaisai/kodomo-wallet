"""
GraphQL schema definition using Strawberry.
"""

import strawberry
from strawberry.types import Info

from app.api.graphql import resolvers
from app.api.graphql.types import Account, Profile, Transaction
from app.core.exceptions import (
    DomainException,
    InvalidAmountException,
    ResourceNotFoundException,
)


@strawberry.type
class Query:
    """GraphQL Query definitions"""

    @strawberry.field
    def me(
        self,
        info: Info,
        user_id: str,
    ) -> Profile | None:
        """Get current user profile"""
        profile_service = info.context["profile_service"]
        return resolvers.get_profile_by_id(user_id, profile_service)

    @strawberry.field
    def accounts(
        self,
        info: Info,
        user_id: str,
    ) -> list[Account]:
        """Get accounts for a user"""
        account_service = info.context["account_service"]
        return resolvers.get_accounts_by_user_id(user_id, account_service)

    @strawberry.field
    def transactions(
        self,
        info: Info,
        account_id: str,
        limit: int = 50,
    ) -> list[Transaction]:
        """Get transactions for an account"""
        transaction_service = info.context["transaction_service"]
        return resolvers.get_transactions_by_account_id(account_id, transaction_service, limit)


@strawberry.type
class Mutation:
    """GraphQL Mutation definitions"""

    @strawberry.mutation
    def deposit(
        self,
        info: Info,
        account_id: str,
        amount: int,
        description: str | None = None,
    ) -> Transaction:
        """Create a deposit transaction"""
        db = info.context["db"]
        transaction_service = info.context["transaction_service"]
        try:
            return resolvers.create_deposit(
                account_id, amount, db, transaction_service, description
            )
        except ResourceNotFoundException as e:
            raise Exception(f"Resource not found: {e.message}") from e
        except InvalidAmountException as e:
            raise Exception(f"Invalid amount: {e.message}") from e
        except DomainException as e:
            raise Exception(f"Domain error: {e.message}") from e


# Create schema
schema = strawberry.Schema(query=Query, mutation=Mutation)

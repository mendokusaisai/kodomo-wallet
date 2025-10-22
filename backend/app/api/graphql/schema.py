"""
GraphQL schema definition using Strawberry.
"""

from typing import List, Optional

import strawberry
from app.api.graphql import resolvers
from app.api.graphql.types import Account, Profile, Transaction
from app.core.database import SessionLocal


def get_context():
    """Get database session for context"""
    return {"db": SessionLocal()}


@strawberry.type
class Query:
    """GraphQL Query definitions"""

    @strawberry.field
    def me(self, info, user_id: str) -> Optional[Profile]:
        """Get current user profile"""
        db = info.context["db"]
        return resolvers.get_profile_by_id(db, user_id)

    @strawberry.field
    def accounts(self, info, user_id: str) -> List[Account]:
        """Get accounts for a user"""
        db = info.context["db"]
        return resolvers.get_accounts_by_user_id(db, user_id)

    @strawberry.field
    def transactions(self, info, account_id: str, limit: int = 50) -> List[Transaction]:
        """Get transactions for an account"""
        db = info.context["db"]
        return resolvers.get_transactions_by_account_id(db, account_id, limit)


@strawberry.type
class Mutation:
    """GraphQL Mutation definitions"""

    @strawberry.mutation
    def deposit(
        self, info, account_id: str, amount: int, description: Optional[str] = None
    ) -> Transaction:
        """Create a deposit transaction"""
        db = info.context["db"]
        try:
            return resolvers.create_deposit(db, account_id, amount, description)
        except ValueError as e:
            raise Exception(str(e))


# Create schema
schema = strawberry.Schema(query=Query, mutation=Mutation)

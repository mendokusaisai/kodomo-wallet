"""
GraphQL schema definition using Strawberry.
"""

import strawberry
from strawberry.types import Info

from app.api.graphql import resolvers
from app.api.graphql.types import Account, Profile, Transaction, WithdrawalRequest
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
        profile_service = info.context["profile_service"]
        return resolvers.get_accounts_by_user_id(user_id, account_service, profile_service)

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

    @strawberry.field
    def withdrawal_requests(
        self,
        info: Info,
        parent_id: str,
    ) -> list[WithdrawalRequest]:
        """Get pending withdrawal requests for a parent's children"""
        withdrawal_request_service = info.context["withdrawal_request_service"]
        return resolvers.get_pending_withdrawal_requests(parent_id, withdrawal_request_service)


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
        transaction_service = info.context["transaction_service"]
        try:
            return resolvers.create_deposit(account_id, amount, transaction_service, description)
        except ResourceNotFoundException as e:
            raise Exception(f"Resource not found: {e.message}") from e
        except InvalidAmountException as e:
            raise Exception(f"Invalid amount: {e.message}") from e
        except DomainException as e:
            raise Exception(f"Domain error: {e.message}") from e

    @strawberry.mutation
    def withdraw(
        self,
        info: Info,
        account_id: str,
        amount: int,
        description: str | None = None,
    ) -> Transaction:
        """Create a withdraw transaction"""
        transaction_service = info.context["transaction_service"]
        try:
            return resolvers.create_withdraw(account_id, amount, transaction_service, description)
        except ResourceNotFoundException as e:
            raise Exception(f"Resource not found: {e.message}") from e
        except InvalidAmountException as e:
            raise Exception(f"Invalid amount: {e.message}") from e
        except DomainException as e:
            raise Exception(f"Domain error: {e.message}") from e

    @strawberry.mutation
    def create_child(
        self,
        info: Info,
        parent_id: str,
        child_name: str,
        initial_balance: int = 0,
    ) -> Profile:
        """Create a child profile without authentication"""
        profile_service = info.context["profile_service"]
        try:
            return resolvers.create_child_profile(
                parent_id, child_name, profile_service, initial_balance
            )
        except ResourceNotFoundException as e:
            raise Exception(f"Resource not found: {e.message}") from e
        except DomainException as e:
            raise Exception(f"Domain error: {e.message}") from e

    @strawberry.mutation
    def link_child_to_auth(
        self,
        info: Info,
        child_id: str,
        auth_user_id: str,
    ) -> Profile:
        """Link child profile to authentication account"""
        profile_service = info.context["profile_service"]
        try:
            return resolvers.link_child_to_auth_account(child_id, auth_user_id, profile_service)
        except ResourceNotFoundException as e:
            raise Exception(f"Resource not found: {e.message}") from e
        except InvalidAmountException as e:
            raise Exception(f"Invalid operation: {e.message}") from e
        except DomainException as e:
            raise Exception(f"Domain error: {e.message}") from e

    @strawberry.mutation
    def link_child_to_auth_by_email(
        self,
        info: Info,
        child_id: str,
        email: str,
    ) -> Profile:
        """Link child profile to authentication account by email address"""
        profile_service = info.context["profile_service"]
        try:
            return resolvers.link_child_to_auth_by_email(child_id, email, profile_service)
        except ResourceNotFoundException as e:
            raise Exception(f"Resource not found: {e.message}") from e
        except InvalidAmountException as e:
            raise Exception(f"Invalid operation: {e.message}") from e
        except DomainException as e:
            raise Exception(f"Domain error: {e.message}") from e

    @strawberry.mutation
    def invite_child_to_auth(
        self,
        info: Info,
        child_id: str,
        email: str,
    ) -> Profile:
        """Send invitation email to child to create authentication account"""
        profile_service = info.context["profile_service"]
        try:
            return resolvers.invite_child_to_auth(child_id, email, profile_service)
        except ResourceNotFoundException as e:
            raise Exception(f"Resource not found: {e.message}") from e
        except InvalidAmountException as e:
            raise Exception(f"Failed to send invitation: {e.message}") from e
        except DomainException as e:
            raise Exception(f"Domain error: {e.message}") from e

    @strawberry.mutation
    def create_withdrawal_request(
        self,
        info: Info,
        account_id: str,
        amount: int,
        description: str | None = None,
    ) -> WithdrawalRequest:
        """Create a withdrawal request (child initiates)"""
        withdrawal_request_service = info.context["withdrawal_request_service"]
        try:
            return resolvers.create_withdrawal_request(
                account_id, amount, withdrawal_request_service, description
            )
        except ResourceNotFoundException as e:
            raise Exception(f"Resource not found: {e.message}") from e
        except InvalidAmountException as e:
            raise Exception(f"Invalid amount: {e.message}") from e
        except DomainException as e:
            raise Exception(f"Domain error: {e.message}") from e

    @strawberry.mutation
    def approve_withdrawal_request(
        self,
        info: Info,
        request_id: str,
    ) -> WithdrawalRequest:
        """Approve a withdrawal request (parent approves)"""
        withdrawal_request_service = info.context["withdrawal_request_service"]
        try:
            return resolvers.approve_withdrawal_request(request_id, withdrawal_request_service)
        except ResourceNotFoundException as e:
            raise Exception(f"Resource not found: {e.message}") from e
        except InvalidAmountException as e:
            raise Exception(f"Invalid operation: {e.message}") from e
        except DomainException as e:
            raise Exception(f"Domain error: {e.message}") from e

    @strawberry.mutation
    def reject_withdrawal_request(
        self,
        info: Info,
        request_id: str,
    ) -> WithdrawalRequest:
        """Reject a withdrawal request (parent rejects)"""
        withdrawal_request_service = info.context["withdrawal_request_service"]
        try:
            return resolvers.reject_withdrawal_request(request_id, withdrawal_request_service)
        except ResourceNotFoundException as e:
            raise Exception(f"Resource not found: {e.message}") from e
        except InvalidAmountException as e:
            raise Exception(f"Invalid operation: {e.message}") from e
        except DomainException as e:
            raise Exception(f"Domain error: {e.message}") from e


# Create schema
schema = strawberry.Schema(query=Query, mutation=Mutation)

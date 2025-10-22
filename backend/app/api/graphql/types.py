"""
GraphQL types for Strawberry.
"""

import strawberry


@strawberry.type
class Profile:
    """User profile type"""

    id: str
    name: str
    role: str
    avatar_url: str | None
    created_at: str
    updated_at: str


@strawberry.type
class Account:
    """Account type"""

    id: str
    user_id: str
    balance: int
    currency: str
    goal_name: str | None
    goal_amount: int | None
    created_at: str
    updated_at: str


@strawberry.type
class Transaction:
    """Transaction type"""

    id: str
    account_id: str
    type: str
    amount: int
    description: str | None
    created_at: str


@strawberry.type
class WithdrawalRequest:
    """Withdrawal request type"""

    id: str
    account_id: str
    amount: int
    description: str | None
    status: str
    created_at: str
    updated_at: str

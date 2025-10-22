"""
GraphQL types for Strawberry.
"""

from typing import Optional

import strawberry


@strawberry.type
class Profile:
    """User profile type"""

    id: str
    name: str
    role: str
    avatar_url: Optional[str]
    created_at: str
    updated_at: str


@strawberry.type
class Account:
    """Account type"""

    id: str
    user_id: str
    balance: int
    currency: str
    goal_name: Optional[str]
    goal_amount: Optional[int]
    created_at: str
    updated_at: str


@strawberry.type
class Transaction:
    """Transaction type"""

    id: str
    account_id: str
    type: str
    amount: int
    description: Optional[str]
    created_at: str


@strawberry.type
class WithdrawalRequest:
    """Withdrawal request type"""

    id: str
    account_id: str
    amount: int
    description: Optional[str]
    status: str
    created_at: str
    updated_at: str

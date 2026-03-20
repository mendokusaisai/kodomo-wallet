"""
StrawberryのGraphQL型定義（家族中心モデル）
"""

from __future__ import annotations

import strawberry


@strawberry.type
class FamilyMemberType:
    """家族メンバー型"""

    uid: str
    family_id: str
    name: str
    role: str
    email: str | None
    joined_at: str


@strawberry.type
class FamilyType:
    """家族型"""

    id: str
    name: str | None
    created_at: str
    members: list[FamilyMemberType]


@strawberry.type
class AccountType:
    """口座型"""

    id: str
    family_id: str
    name: str
    balance: int
    currency: str
    goal_name: str | None
    goal_amount: int | None
    created_at: str
    updated_at: str


@strawberry.type
class TransactionType:
    """トランザクション型"""

    id: str
    account_id: str
    family_id: str
    type: str
    amount: int
    note: str | None
    created_at: str
    created_by_uid: str


@strawberry.type
class RecurringDepositType:
    """定期入金型"""

    id: str
    family_id: str
    account_id: str
    amount: int
    interval_days: int
    next_execute_at: str
    is_active: bool
    created_at: str
    created_by_uid: str

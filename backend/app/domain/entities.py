"""
ドメインエンティティ - 永続化技術に依存しないビジネスモデル
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal


@dataclass
class Profile:
    """ユーザープロフィールエンティティ"""

    id: str
    auth_user_id: str | None
    email: str | None
    name: str
    role: Literal["parent", "child"]
    avatar_url: str | None
    created_at: datetime
    updated_at: datetime


@dataclass
class Account:
    """アカウントエンティティ"""

    id: str
    user_id: str
    balance: int
    currency: str
    goal_name: str | None
    goal_amount: int | None
    created_at: datetime
    updated_at: datetime


@dataclass
class Transaction:
    """トランザクションエンティティ"""

    id: str
    account_id: str
    type: Literal["deposit", "withdraw", "reward"]
    amount: int
    description: str | None
    created_at: datetime


@dataclass
class WithdrawalRequest:
    """出金リクエストエンティティ"""

    id: str
    account_id: str
    amount: int
    description: str | None
    status: Literal["pending", "approved", "rejected"]
    created_at: datetime
    updated_at: datetime


@dataclass
class RecurringDeposit:
    """定期入金エンティティ（自動お小遣い）"""

    id: str
    account_id: str
    amount: int
    day_of_month: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


@dataclass
class FamilyRelationship:
    """家族関係エンティティ（親-子の多対多関係）"""

    id: str
    parent_id: str
    child_id: str
    relationship_type: Literal["parent", "guardian"]
    created_at: datetime


@dataclass
class ParentInvite:
    """親招待エンティティ"""

    id: str
    token: str
    child_id: str
    inviter_id: str
    email: str
    status: Literal["pending", "accepted", "expired", "cancelled"]
    expires_at: datetime
    created_at: datetime

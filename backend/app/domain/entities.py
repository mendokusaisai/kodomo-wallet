"""
ドメインエンティティ - 永続化技術に依存しないビジネスモデル

家族中心の設計: 口座は特定メンバーに紐づかず家族全体のリソース
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal


@dataclass
class Family:
    """家族エンティティ"""

    id: str
    name: str | None
    created_at: datetime


@dataclass
class FamilyMember:
    """家族メンバーエンティティ（ドキュメントIDは Firebase Auth UID）"""

    uid: str
    family_id: str
    name: str
    role: Literal["parent", "child"]
    email: str | None  # 親のみ
    joined_at: datetime
    updated_at: datetime


@dataclass
class Account:
    """口座エンティティ（家族直下。特定メンバーへの紐づけなし）"""

    id: str
    family_id: str
    name: str
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
    family_id: str
    type: Literal["deposit", "withdraw", "reward"]
    amount: int
    note: str | None
    created_at: datetime
    created_by_uid: str


@dataclass
class RecurringDeposit:
    """定期入金エンティティ（自動お小遣い）"""

    id: str
    family_id: str
    account_id: str
    amount: int
    interval_days: int
    next_execute_at: datetime
    is_active: bool
    created_at: datetime
    created_by_uid: str


@dataclass
class ParentInvite:
    """親招待エンティティ（子が親を家族に招待）"""

    token: str
    family_id: str
    inviter_uid: str
    email: str
    expires_at: datetime
    accepted_at: datetime | None
    created_at: datetime


@dataclass
class ChildInvite:
    """子招待エンティティ（親が子を家族に招待）"""

    token: str
    family_id: str
    inviter_uid: str
    child_name: str
    expires_at: datetime
    accepted_at: datetime | None
    created_at: datetime


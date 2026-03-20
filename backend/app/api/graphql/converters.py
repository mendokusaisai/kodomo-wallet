"""
ドメインエンティティをGraphQL型に変換するコンバーター（家族中心モデル）
"""

from datetime import datetime

from app.api.graphql import types as t
from app.domain import entities as e


def _dt(dt: datetime | str) -> str:
    """datetime または文字列を ISO 形式に変換"""
    if isinstance(dt, str):
        return dt
    return dt.isoformat()


def to_family_member(entity: e.FamilyMember) -> t.FamilyMemberType:
    return t.FamilyMemberType(
        uid=entity.uid,
        family_id=entity.family_id,
        name=entity.name,
        role=entity.role,
        email=entity.email,
        joined_at=_dt(entity.joined_at),
    )


def to_family(entity: e.Family, members: list[e.FamilyMember]) -> t.FamilyType:
    return t.FamilyType(
        id=entity.id,
        name=entity.name,
        created_at=_dt(entity.created_at),
        members=[to_family_member(m) for m in members],
    )


def to_account(entity: e.Account) -> t.AccountType:
    return t.AccountType(
        id=entity.id,
        family_id=entity.family_id,
        name=entity.name,
        balance=entity.balance,
        currency=entity.currency,
        goal_name=entity.goal_name,
        goal_amount=entity.goal_amount,
        created_at=_dt(entity.created_at),
        updated_at=_dt(entity.updated_at),
    )


def to_transaction(entity: e.Transaction) -> t.TransactionType:
    return t.TransactionType(
        id=entity.id,
        account_id=entity.account_id,
        family_id=entity.family_id,
        type=entity.type,
        amount=entity.amount,
        note=entity.note,
        created_at=_dt(entity.created_at),
        created_by_uid=entity.created_by_uid,
    )


def to_recurring_deposit(entity: e.RecurringDeposit) -> t.RecurringDepositType:
    return t.RecurringDepositType(
        id=entity.id,
        family_id=entity.family_id,
        account_id=entity.account_id,
        amount=entity.amount,
        interval_days=entity.interval_days,
        next_execute_at=_dt(entity.next_execute_at),
        is_active=entity.is_active,
        created_at=_dt(entity.created_at),
        created_by_uid=entity.created_by_uid,
    )

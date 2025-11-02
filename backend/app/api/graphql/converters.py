"""
ドメインエンティティをGraphQL型に変換するコンバーター
"""

from datetime import datetime

from app.api.graphql import types as graphql_types
from app.domain import entities as domain_entities


def _to_iso_string(dt: datetime | str) -> str:
    """datetimeまたは文字列をISO形式の文字列に変換"""
    if isinstance(dt, str):
        return dt
    return dt.isoformat()


def to_graphql_profile(entity: domain_entities.Profile) -> graphql_types.Profile:
    """ドメインのProfileをGraphQL型に変換"""
    return graphql_types.Profile(
        id=str(entity.id),
        name=entity.name,
        role=entity.role,
        avatar_url=entity.avatar_url,
        created_at=_to_iso_string(entity.created_at),
        updated_at=_to_iso_string(entity.updated_at),
        auth_user_id=entity.auth_user_id,
        email=entity.email,
        parent_id=entity.parent_id,
    )


def to_graphql_account(entity: domain_entities.Account) -> graphql_types.Account:
    """ドメインのAccountをGraphQL型に変換"""
    return graphql_types.Account(
        id=str(entity.id),
        user_id=str(entity.user_id),
        balance=entity.balance,
        currency=entity.currency,
        goal_name=entity.goal_name,
        goal_amount=entity.goal_amount,
        created_at=_to_iso_string(entity.created_at),
        updated_at=_to_iso_string(entity.updated_at),
        user=None,  # リゾルバー側で設定
    )


def to_graphql_transaction(entity: domain_entities.Transaction) -> graphql_types.Transaction:
    """ドメインのTransactionをGraphQL型に変換"""
    return graphql_types.Transaction(
        id=str(entity.id),
        account_id=str(entity.account_id),
        type=entity.type,
        amount=entity.amount,
        description=entity.description,
        created_at=_to_iso_string(entity.created_at),
    )


def to_graphql_withdrawal_request(
    entity: domain_entities.WithdrawalRequest,
) -> graphql_types.WithdrawalRequest:
    """ドメインのWithdrawalRequestをGraphQL型に変換"""
    return graphql_types.WithdrawalRequest(
        id=str(entity.id),
        account_id=str(entity.account_id),
        amount=entity.amount,
        description=entity.description,
        status=entity.status,
        created_at=_to_iso_string(entity.created_at),
        updated_at=_to_iso_string(entity.updated_at),
    )


def to_graphql_recurring_deposit(
    entity: domain_entities.RecurringDeposit,
) -> graphql_types.RecurringDeposit:
    """ドメインのRecurringDepositをGraphQL型に変換"""
    return graphql_types.RecurringDeposit(
        id=str(entity.id),
        account_id=str(entity.account_id),
        amount=entity.amount,
        day_of_month=entity.day_of_month,
        is_active=entity.is_active,
        created_at=_to_iso_string(entity.created_at),
        updated_at=_to_iso_string(entity.updated_at),
    )

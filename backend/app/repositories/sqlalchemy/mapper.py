"""
SQLAlchemyモデルとドメインエンティティ間のマッピングユーティリティ
"""

from datetime import datetime

from app.domain import entities as domain
from app.repositories.sqlalchemy import models as db_models


def parse_datetime(dt_str: str | datetime) -> datetime:
    """文字列またはdatetimeオブジェクトからdatetimeオブジェクトを生成"""
    # 既にdatetimeオブジェクトの場合はそのまま返す
    if isinstance(dt_str, datetime):
        return dt_str
    # ISO 8601形式の文字列をパース
    return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))


def to_domain_profile(db_profile: db_models.Profile) -> domain.Profile:
    """SQLAlchemyのProfileモデルをドメインエンティティに変換"""
    return domain.Profile(
        id=str(db_profile.id),
        auth_user_id=str(db_profile.auth_user_id) if db_profile.auth_user_id is not None else None,
        email=None,  # 必要な時だけSupabaseから取得
        name=str(db_profile.name),  # type: ignore
        role=db_profile.role,  # type: ignore
        avatar_url=str(db_profile.avatar_url) if db_profile.avatar_url is not None else None,  # type: ignore
        created_at=parse_datetime(db_profile.created_at),  # type: ignore
        updated_at=parse_datetime(db_profile.updated_at),  # type: ignore
    )


def to_domain_account(db_account: db_models.Account) -> domain.Account:
    """SQLAlchemyのAccountモデルをドメインエンティティに変換"""
    return domain.Account(
        id=str(db_account.id),
        user_id=str(db_account.user_id),
        balance=int(db_account.balance),  # type: ignore
        currency=str(db_account.currency),  # type: ignore
        goal_name=str(db_account.goal_name) if db_account.goal_name is not None else None,  # type: ignore
        goal_amount=int(db_account.goal_amount) if db_account.goal_amount is not None else None,  # type: ignore
        created_at=parse_datetime(db_account.created_at),  # type: ignore
        updated_at=parse_datetime(db_account.updated_at),  # type: ignore
    )


def to_domain_transaction(db_transaction: db_models.Transaction) -> domain.Transaction:
    """SQLAlchemyのTransactionモデルをドメインエンティティに変換"""
    return domain.Transaction(
        id=str(db_transaction.id),
        account_id=str(db_transaction.account_id),
        type=db_transaction.type,  # type: ignore
        amount=int(db_transaction.amount),  # type: ignore
        description=str(db_transaction.description)
        if db_transaction.description is not None
        else None,  # type: ignore
        created_at=parse_datetime(db_transaction.created_at),  # type: ignore
    )


def to_domain_withdrawal_request(
    db_request: db_models.WithdrawalRequest,
) -> domain.WithdrawalRequest:
    """SQLAlchemyのWithdrawalRequestモデルをドメインエンティティに変換"""
    return domain.WithdrawalRequest(
        id=str(db_request.id),
        account_id=str(db_request.account_id),
        amount=int(db_request.amount),  # type: ignore
        description=str(db_request.description) if db_request.description is not None else None,  # type: ignore
        status=db_request.status,  # type: ignore
        created_at=parse_datetime(db_request.created_at),  # type: ignore
        updated_at=parse_datetime(db_request.updated_at),  # type: ignore
    )


def to_domain_recurring_deposit(
    db_deposit: db_models.RecurringDeposit,
) -> domain.RecurringDeposit:
    """SQLAlchemyのRecurringDepositモデルをドメインエンティティに変換"""
    return domain.RecurringDeposit(
        id=str(db_deposit.id),
        account_id=str(db_deposit.account_id),
        amount=int(db_deposit.amount),  # type: ignore
        day_of_month=int(db_deposit.day_of_month),  # type: ignore
        is_active=db_deposit.is_active == "true",  # type: ignore
        created_at=parse_datetime(db_deposit.created_at),  # type: ignore
        updated_at=parse_datetime(db_deposit.updated_at),  # type: ignore
    )


def to_domain_family_relationship(
    db_relationship: db_models.FamilyRelationship,
) -> domain.FamilyRelationship:
    """SQLAlchemyのFamilyRelationshipモデルをドメインエンティティに変換"""
    return domain.FamilyRelationship(
        id=str(db_relationship.id),
        parent_id=str(db_relationship.parent_id),
        child_id=str(db_relationship.child_id),
        relationship_type=str(db_relationship.relationship_type),  # type: ignore
        created_at=parse_datetime(db_relationship.created_at),  # type: ignore
    )


def to_domain_parent_invite(db_invite: db_models.ParentInvite) -> domain.ParentInvite:
    """SQLAlchemyのParentInviteモデルをドメインエンティティに変換"""
    return domain.ParentInvite(
        id=str(db_invite.id),
        token=str(db_invite.token),
        child_id=str(db_invite.child_id),
        inviter_id=str(db_invite.inviter_id),
        email=str(db_invite.email),
        status=db_invite.status,  # type: ignore
        expires_at=parse_datetime(db_invite.expires_at),  # type: ignore
        created_at=parse_datetime(db_invite.created_at),  # type: ignore
    )


def to_domain_child_invite(db_invite: db_models.ChildInvite) -> domain.ChildInvite:
    """SQLAlchemyのChildInviteモデルをドメインエンティティに変換"""
    return domain.ChildInvite(
        id=str(db_invite.id),
        token=str(db_invite.token),
        child_id=str(db_invite.child_id),
        email=str(db_invite.email),
        status=db_invite.status,  # type: ignore
        expires_at=parse_datetime(db_invite.expires_at),  # type: ignore
        created_at=parse_datetime(db_invite.created_at),  # type: ignore
    )

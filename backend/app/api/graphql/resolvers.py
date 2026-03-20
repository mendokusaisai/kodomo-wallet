"""
クエリとミューテーションのGraphQLリゾルバー（家族中心モデル）
"""

from app.api.graphql import converters
from app.api.graphql.types import (
    AccountType,
    FamilyMemberType,
    FamilyType,
    TransactionType,
)
from app.services import AccountService, FamilyService, TransactionService


# ── Queries ──────────────────────────────────────────────────────────────────────────────────

def get_my_family(uid: str, family_service: FamilyService) -> FamilyType | None:
    """自分が属する家族を返す"""
    member = family_service.get_member(uid)
    if not member:
        return None
    family = family_service.get_family(member.family_id)
    if not family:
        return None
    members = family_service.get_members(family.id)
    return converters.to_family(family, members)


def get_family_accounts(family_id: str, account_service: AccountService) -> list[AccountType]:
    """家族の口座一覧を返す"""
    entities = account_service.get_family_accounts(family_id)
    return [converters.to_account(e) for e in entities]


def get_account_transactions(
    family_id: str,
    account_id: str,
    transaction_service: TransactionService,
    limit: int = 50,
) -> list[TransactionType]:
    """口座のトランザクション一覧を返す"""
    entities = transaction_service.get_account_transactions(family_id, account_id, limit)
    return [converters.to_transaction(e) for e in entities]



# ── Mutations ─────────────────────────────────────────────────────────────────────────────────
def create_family(
    uid: str,
    my_name: str,
    email: str,
    family_service: FamilyService,
    family_name: str | None = None,
) -> FamilyType:
    """家族を新規作成し呼び出し元を親として追加"""
    family, member = family_service.create_family_with_parent(
        uid=uid, name=my_name, email=email, family_name=family_name
    )
    return converters.to_family(family, [member])


def invite_parent(
    family_id: str,
    inviter_uid: str,
    email: str,
    family_service: FamilyService,
) -> str:
    """親招待トークンを発行"""
    invite = family_service.invite_parent(family_id, inviter_uid, email)
    return invite.token


def invite_child(
    family_id: str,
    inviter_uid: str,
    child_name: str,
    family_service: FamilyService,
) -> str:
    """子招待トークンを発行"""
    invite = family_service.invite_child(family_id, inviter_uid, child_name)
    return invite.token


def join_as_parent(
    token: str,
    uid: str,
    name: str,
    email: str,
    family_service: FamilyService,
) -> FamilyMemberType:
    """親招待を承認して家族に参加"""
    member = family_service.accept_parent_invite(token=token, uid=uid, name=name, email=email)
    return converters.to_family_member(member)


def join_as_child(
    token: str,
    uid: str,
    family_service: FamilyService,
) -> FamilyMemberType:
    """子招待を承認して家族に参加"""
    member = family_service.accept_child_invite(token=token, uid=uid)
    return converters.to_family_member(member)


def create_account(
    family_id: str,
    current_uid: str,
    name: str,
    account_service: AccountService,
    currency: str = "JPY",
) -> AccountType:
    """口座を新規作成（親のみ）"""
    entity = account_service.create_account(
        family_id=family_id, name=name, current_uid=current_uid, currency=currency
    )
    return converters.to_account(entity)


def deposit(
    family_id: str,
    account_id: str,
    current_uid: str,
    amount: int,
    transaction_service: TransactionService,
    note: str | None = None,
) -> TransactionType:
    """入金トランザクションを作成（親のみ）"""
    entity = transaction_service.create_deposit(
        family_id=family_id,
        account_id=account_id,
        current_uid=current_uid,
        amount=amount,
        note=note,
    )
    return converters.to_transaction(entity)


def withdraw(
    family_id: str,
    account_id: str,
    current_uid: str,
    amount: int,
    transaction_service: TransactionService,
    note: str | None = None,
) -> TransactionType:
    """出金トランザクションを作成（親のみ）"""
    entity = transaction_service.create_withdraw(
        family_id=family_id,
        account_id=account_id,
        current_uid=current_uid,
        amount=amount,
        note=note,
    )
    return converters.to_transaction(entity)


def update_goal(
    family_id: str,
    account_id: str,
    current_uid: str,
    account_service: AccountService,
    goal_name: str | None = None,
    goal_amount: int | None = None,
) -> AccountType:
    """口座の貯金目標を更新（親のみ）"""
    entity = account_service.update_goal(
        family_id=family_id,
        account_id=account_id,
        current_uid=current_uid,
        goal_name=goal_name,
        goal_amount=goal_amount,
    )
    return converters.to_account(entity)




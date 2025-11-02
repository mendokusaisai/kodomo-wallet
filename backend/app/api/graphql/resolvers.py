"""
クエリとミューテーションのGraphQLリゾルバー

これらのリゾルバーはデータベースの詳細を知ることなく、サービス層の依存性を使用します。
"""

from app.api.graphql import converters
from app.api.graphql.types import Account, Profile, RecurringDeposit, Transaction, WithdrawalRequest
from app.services import (
    AccountService,
    ProfileService,
    RecurringDepositService,
    TransactionService,
    WithdrawalRequestService,
)


def get_profile_by_id(
    user_id: str,
    profile_service: ProfileService,
) -> Profile | None:
    """IDでユーザープロフィールを取得"""
    entity = profile_service.get_profile(user_id)
    return converters.to_graphql_profile(entity) if entity else None


def get_children_count(
    parent_id: str,
    profile_service: ProfileService,
) -> int:
    """親の子供の数を取得"""
    children = profile_service.get_children(parent_id)
    return len(children)


def get_accounts_by_user_id(
    user_id: str,
    account_service: AccountService,
    profile_service: ProfileService,
) -> list[Account]:
    """ユーザーとその子供（親の場合）の全アカウントを取得"""
    entities = account_service.get_family_accounts(user_id)

    # エンティティをGraphQL型に変換し、各アカウントにユーザー情報を付与
    accounts = []
    for entity in entities:
        account = converters.to_graphql_account(entity)
        user_entity = profile_service.get_profile(str(entity.user_id))
        if user_entity:
            account.user = converters.to_graphql_profile(user_entity)
        accounts.append(account)

    return accounts


def get_transactions_by_account_id(
    account_id: str,
    transaction_service: TransactionService,
    limit: int = 50,
) -> list[Transaction]:
    """指定したアカウントのトランザクション一覧を取得"""
    entities = transaction_service.get_account_transactions(account_id, limit)
    return [converters.to_graphql_transaction(e) for e in entities]


def create_deposit(
    account_id: str,
    amount: int,
    transaction_service: TransactionService,
    description: str | None = None,
) -> Transaction:
    """入金（deposit）トランザクションを作成"""
    entity = transaction_service.create_deposit(account_id, amount, description)
    return converters.to_graphql_transaction(entity)


def create_withdraw(
    account_id: str,
    amount: int,
    transaction_service: TransactionService,
    description: str | None = None,
) -> Transaction:
    """出金（withdraw）トランザクションを作成"""
    entity = transaction_service.create_withdraw(account_id, amount, description)
    return converters.to_graphql_transaction(entity)


def create_child_profile(
    parent_id: str,
    child_name: str,
    profile_service: ProfileService,
    initial_balance: int = 0,
) -> Profile:
    """認証なしで子プロフィールを作成"""
    entity = profile_service.create_child(parent_id, child_name, initial_balance)
    return converters.to_graphql_profile(entity)


def link_child_to_auth_account(
    child_id: str,
    auth_user_id: str,
    profile_service: ProfileService,
) -> Profile:
    """子プロフィールを認証アカウントに紐付け"""
    entity = profile_service.link_child_to_auth(child_id, auth_user_id)
    return converters.to_graphql_profile(entity)


def link_child_to_auth_by_email(
    child_id: str,
    email: str,
    profile_service: ProfileService,
) -> Profile:
    """メールアドレスで子プロフィールを認証アカウントに紐付け"""
    entity = profile_service.link_child_to_auth_by_email(child_id, email)
    return converters.to_graphql_profile(entity)


def invite_child_to_auth(
    child_id: str,
    email: str,
    profile_service: ProfileService,
) -> Profile:
    """メール経由で子に認証アカウント作成を招待"""
    entity = profile_service.invite_child_to_auth(child_id, email)
    return converters.to_graphql_profile(entity)


def get_pending_withdrawal_requests(
    parent_id: str,
    withdrawal_request_service: WithdrawalRequestService,
) -> list[WithdrawalRequest]:
    """親ユーザーの子供に対する未承認の出金リクエストを取得"""
    entities = withdrawal_request_service.get_pending_requests_for_parent(parent_id)
    return [converters.to_graphql_withdrawal_request(e) for e in entities]


def create_withdrawal_request(
    account_id: str,
    amount: int,
    withdrawal_request_service: WithdrawalRequestService,
    description: str | None = None,
) -> WithdrawalRequest:
    """出金リクエストを作成（子が発行）"""
    entity = withdrawal_request_service.create_withdrawal_request(account_id, amount, description)
    return converters.to_graphql_withdrawal_request(entity)


def approve_withdrawal_request(
    request_id: str,
    withdrawal_request_service: WithdrawalRequestService,
    transaction_service: TransactionService,
) -> WithdrawalRequest:
    """出金リクエストを承認（親が承認）"""
    entity = withdrawal_request_service.approve_withdrawal_request(request_id, transaction_service)
    return converters.to_graphql_withdrawal_request(entity)


def reject_withdrawal_request(
    request_id: str,
    withdrawal_request_service: WithdrawalRequestService,
) -> WithdrawalRequest:
    """出金リクエストを却下（親が却下）"""
    entity = withdrawal_request_service.reject_withdrawal_request(request_id)
    return converters.to_graphql_withdrawal_request(entity)


def update_goal(
    account_id: str,
    goal_name: str | None,
    goal_amount: int | None,
    account_service: AccountService,
) -> Account:
    """アカウントの貯金目標を更新"""
    entity = account_service.update_goal(account_id, goal_name, goal_amount)
    return converters.to_graphql_account(entity)


def update_profile(
    user_id: str,
    current_user_id: str,
    name: str | None,
    avatar_url: str | None,
    profile_service: ProfileService,
) -> Profile:
    """ユーザープロフィールを更新（本人または親が子を編集可能）"""
    entity = profile_service.update_profile(user_id, current_user_id, name, avatar_url)
    return converters.to_graphql_profile(entity)


def delete_child(
    parent_id: str,
    child_id: str,
    profile_service: ProfileService,
) -> bool:
    """子プロフィールを削除（親のみ実行可能）"""
    return profile_service.delete_child(parent_id, child_id)


def get_recurring_deposit(
    account_id: str,
    current_user_id: str,
    recurring_deposit_service: RecurringDepositService,
) -> RecurringDeposit | None:
    """アカウントの定期入金設定を取得（親のみ）"""
    entity = recurring_deposit_service.get_recurring_deposit(account_id, current_user_id)
    return converters.to_graphql_recurring_deposit(entity) if entity else None


def create_or_update_recurring_deposit(
    account_id: str,
    current_user_id: str,
    amount: int,
    day_of_month: int,
    recurring_deposit_service: RecurringDepositService,
    is_active: bool = True,
) -> RecurringDeposit:
    """定期入金設定を作成または更新（親のみ）"""
    entity = recurring_deposit_service.create_or_update_recurring_deposit(
        account_id, current_user_id, amount, day_of_month, is_active
    )
    return converters.to_graphql_recurring_deposit(entity)


def delete_recurring_deposit(
    account_id: str,
    current_user_id: str,
    recurring_deposit_service: RecurringDepositService,
) -> bool:
    """定期入金設定を削除（親のみ）"""
    return recurring_deposit_service.delete_recurring_deposit(account_id, current_user_id)


# ===== 親招待（メール/リンク） =====
def create_parent_invite(
    inviter_id: str,
    email: str,
    profile_service: ProfileService,
) -> str:
    """親を招待するためのトークン(文字列)を返す。招待者の全ての子どもと受理者が紐づけられる"""
    return profile_service.create_parent_invite(inviter_id, email)


def accept_parent_invite(
    token: str,
    current_parent_id: str,
    profile_service: ProfileService,
) -> bool:
    """親招待を受理し、親子関係を作成する"""
    return profile_service.accept_parent_invite(token, current_parent_id)

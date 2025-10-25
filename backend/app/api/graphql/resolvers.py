"""
クエリとミューテーションのGraphQLリゾルバー

これらのリゾルバーはデータベースの詳細を知ることなく、サービス層の依存性を使用します。
"""

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
    return profile_service.get_profile(user_id)


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
    accounts = account_service.get_family_accounts(user_id)

    # 各アカウントにユーザー情報を付与
    for account in accounts:
        user_profile = profile_service.get_profile(str(account.user_id))
        if user_profile:
            account.user = user_profile

    return accounts


def get_transactions_by_account_id(
    account_id: str,
    transaction_service: TransactionService,
    limit: int = 50,
) -> list[Transaction]:
    """Get transactions for an account"""
    return transaction_service.get_account_transactions(account_id, limit)


def create_deposit(
    account_id: str,
    amount: int,
    transaction_service: TransactionService,
    description: str | None = None,
) -> Transaction:
    """Create a deposit transaction"""
    return transaction_service.create_deposit(account_id, amount, description)


def create_withdraw(
    account_id: str,
    amount: int,
    transaction_service: TransactionService,
    description: str | None = None,
) -> Transaction:
    """Create a withdraw transaction"""
    return transaction_service.create_withdraw(account_id, amount, description)


def create_child_profile(
    parent_id: str,
    child_name: str,
    profile_service: ProfileService,
    initial_balance: int = 0,
) -> Profile:
    """Create a child profile without authentication"""
    return profile_service.create_child(parent_id, child_name, initial_balance)


def link_child_to_auth_account(
    child_id: str,
    auth_user_id: str,
    profile_service: ProfileService,
) -> Profile:
    """Link child profile to authentication account"""
    return profile_service.link_child_to_auth(child_id, auth_user_id)


def link_child_to_auth_by_email(
    child_id: str,
    email: str,
    profile_service: ProfileService,
) -> Profile:
    """Link child profile to authentication account by email"""
    return profile_service.link_child_to_auth_by_email(child_id, email)


def invite_child_to_auth(
    child_id: str,
    email: str,
    profile_service: ProfileService,
) -> Profile:
    """Invite child to create authentication account via email"""
    return profile_service.invite_child_to_auth(child_id, email)


def get_pending_withdrawal_requests(
    parent_id: str,
    withdrawal_request_service: WithdrawalRequestService,
) -> list[WithdrawalRequest]:
    """Get pending withdrawal requests for a parent's children"""
    return withdrawal_request_service.get_pending_requests_for_parent(parent_id)


def create_withdrawal_request(
    account_id: str,
    amount: int,
    withdrawal_request_service: WithdrawalRequestService,
    description: str | None = None,
) -> WithdrawalRequest:
    """Create a withdrawal request (child initiates)"""
    return withdrawal_request_service.create_withdrawal_request(account_id, amount, description)


def approve_withdrawal_request(
    request_id: str,
    withdrawal_request_service: WithdrawalRequestService,
    transaction_service: TransactionService,
) -> WithdrawalRequest:
    """Approve a withdrawal request (parent approves)"""
    return withdrawal_request_service.approve_withdrawal_request(request_id, transaction_service)


def reject_withdrawal_request(
    request_id: str,
    withdrawal_request_service: WithdrawalRequestService,
) -> WithdrawalRequest:
    """Reject a withdrawal request (parent rejects)"""
    return withdrawal_request_service.reject_withdrawal_request(request_id)


def update_goal(
    account_id: str,
    goal_name: str | None,
    goal_amount: int | None,
    account_service: AccountService,
) -> Account:
    """Update savings goal for an account"""
    return account_service.update_goal(account_id, goal_name, goal_amount)


def update_profile(
    user_id: str,
    current_user_id: str,
    name: str | None,
    avatar_url: str | None,
    profile_service: ProfileService,
) -> Profile:
    """Update user profile (self or parent can edit child)"""
    return profile_service.update_profile(user_id, current_user_id, name, avatar_url)


def delete_child(
    parent_id: str,
    child_id: str,
    profile_service: ProfileService,
) -> bool:
    """Delete a child profile (parent only)"""
    return profile_service.delete_child(parent_id, child_id)


def get_recurring_deposit(
    account_id: str,
    current_user_id: str,
    recurring_deposit_service: RecurringDepositService,
) -> RecurringDeposit | None:
    """Get recurring deposit settings for an account (parent only)"""
    return recurring_deposit_service.get_recurring_deposit(account_id, current_user_id)


def create_or_update_recurring_deposit(
    account_id: str,
    current_user_id: str,
    amount: int,
    day_of_month: int,
    recurring_deposit_service: RecurringDepositService,
    is_active: bool = True,
) -> RecurringDeposit:
    """Create or update recurring deposit settings (parent only)"""
    return recurring_deposit_service.create_or_update_recurring_deposit(
        account_id, current_user_id, amount, day_of_month, is_active
    )


def delete_recurring_deposit(
    account_id: str,
    current_user_id: str,
    recurring_deposit_service: RecurringDepositService,
) -> bool:
    """Delete recurring deposit settings (parent only)"""
    return recurring_deposit_service.delete_recurring_deposit(account_id, current_user_id)

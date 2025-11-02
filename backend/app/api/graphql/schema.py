"""
StrawberryによるGraphQLスキーマ定義
"""

import strawberry
from strawberry.types import Info

from app.api.graphql import resolvers
from app.api.graphql.types import Account, Profile, RecurringDeposit, Transaction, WithdrawalRequest
from app.core.exceptions import (
    DomainException,
    InvalidAmountException,
    ResourceNotFoundException,
)


@strawberry.type
class Query:
    """GraphQL クエリ定義"""

    @strawberry.field
    def me(
        self,
        info: Info,
        user_id: str,
    ) -> Profile | None:
        """現在のユーザープロフィールを取得"""
        profile_service = info.context["profile_service"]
        return resolvers.get_profile_by_id(user_id, profile_service)

    @strawberry.field
    def children_count(
        self,
        info: Info,
        parent_id: str,
    ) -> int:
        """親ユーザーの子供の人数を取得"""
        profile_service = info.context["profile_service"]
        return resolvers.get_children_count(parent_id, profile_service)

    @strawberry.field
    def accounts(
        self,
        info: Info,
        user_id: str,
    ) -> list[Account]:
        """ユーザーのアカウント一覧を取得（親は子のアカウントも含む）"""
        account_service = info.context["account_service"]
        profile_service = info.context["profile_service"]
        return resolvers.get_accounts_by_user_id(user_id, account_service, profile_service)

    @strawberry.field
    def transactions(
        self,
        info: Info,
        account_id: str,
        limit: int = 50,
    ) -> list[Transaction]:
        """アカウントのトランザクション一覧を取得"""
        transaction_service = info.context["transaction_service"]
        return resolvers.get_transactions_by_account_id(account_id, transaction_service, limit)

    @strawberry.field
    def withdrawal_requests(
        self,
        info: Info,
        parent_id: str,
    ) -> list[WithdrawalRequest]:
        """親ユーザーの子供に対する未承認の出金リクエスト一覧を取得"""
        withdrawal_request_service = info.context["withdrawal_request_service"]
        return resolvers.get_pending_withdrawal_requests(parent_id, withdrawal_request_service)

    @strawberry.field
    def recurring_deposit(
        self,
        info: Info,
        account_id: str,
        current_user_id: str,
    ) -> RecurringDeposit | None:
        """アカウントの定期入金設定を取得（親のみ）"""
        recurring_deposit_service = info.context["recurring_deposit_service"]
        try:
            return resolvers.get_recurring_deposit(
                account_id, current_user_id, recurring_deposit_service
            )
        except ResourceNotFoundException as e:
            raise Exception(f"Resource not found: {e.message}") from e
        except InvalidAmountException as e:
            raise Exception(f"Permission denied: {e.message}") from e
        except DomainException as e:
            raise Exception(f"Domain error: {e.message}") from e


@strawberry.type
class Mutation:
    """GraphQL ミューテーション定義"""

    @strawberry.mutation
    def deposit(
        self,
        info: Info,
        account_id: str,
        amount: int,
        description: str | None = None,
    ) -> Transaction:
        """入金（deposit）トランザクションを作成"""
        transaction_service = info.context["transaction_service"]
        try:
            return resolvers.create_deposit(account_id, amount, transaction_service, description)
        except ResourceNotFoundException as e:
            raise Exception(f"Resource not found: {e.message}") from e
        except InvalidAmountException as e:
            raise Exception(f"Invalid amount: {e.message}") from e
        except DomainException as e:
            raise Exception(f"Domain error: {e.message}") from e

    @strawberry.mutation
    def withdraw(
        self,
        info: Info,
        account_id: str,
        amount: int,
        description: str | None = None,
    ) -> Transaction:
        """出金（withdraw）トランザクションを作成"""
        transaction_service = info.context["transaction_service"]
        try:
            return resolvers.create_withdraw(account_id, amount, transaction_service, description)
        except ResourceNotFoundException as e:
            raise Exception(f"Resource not found: {e.message}") from e
        except InvalidAmountException as e:
            raise Exception(f"Invalid amount: {e.message}") from e
        except DomainException as e:
            raise Exception(f"Domain error: {e.message}") from e

    @strawberry.mutation
    def create_child(
        self,
        info: Info,
        parent_id: str,
        child_name: str,
        initial_balance: int = 0,
    ) -> Profile:
        """認証なしで子プロフィールを作成"""
        profile_service = info.context["profile_service"]
        try:
            return resolvers.create_child_profile(
                parent_id, child_name, profile_service, initial_balance
            )
        except ResourceNotFoundException as e:
            raise Exception(f"Resource not found: {e.message}") from e
        except DomainException as e:
            raise Exception(f"Domain error: {e.message}") from e

    @strawberry.mutation
    def link_child_to_auth(
        self,
        info: Info,
        child_id: str,
        auth_user_id: str,
    ) -> Profile:
        """子プロフィールを認証アカウントに紐付け"""
        profile_service = info.context["profile_service"]
        try:
            return resolvers.link_child_to_auth_account(child_id, auth_user_id, profile_service)
        except ResourceNotFoundException as e:
            raise Exception(f"Resource not found: {e.message}") from e
        except InvalidAmountException as e:
            raise Exception(f"Invalid operation: {e.message}") from e
        except DomainException as e:
            raise Exception(f"Domain error: {e.message}") from e

    @strawberry.mutation
    def link_child_to_auth_by_email(
        self,
        info: Info,
        child_id: str,
        email: str,
    ) -> Profile:
        """メールアドレスで子プロフィールを認証アカウントに紐付け"""
        profile_service = info.context["profile_service"]
        try:
            return resolvers.link_child_to_auth_by_email(child_id, email, profile_service)
        except ResourceNotFoundException as e:
            raise Exception(f"Resource not found: {e.message}") from e
        except InvalidAmountException as e:
            raise Exception(f"Invalid operation: {e.message}") from e
        except DomainException as e:
            raise Exception(f"Domain error: {e.message}") from e

    @strawberry.mutation
    def invite_child_to_auth(
        self,
        info: Info,
        child_id: str,
        email: str,
    ) -> Profile:
        """子に認証アカウント作成を促す招待メールを送信"""
        profile_service = info.context["profile_service"]
        try:
            return resolvers.invite_child_to_auth(child_id, email, profile_service)
        except ResourceNotFoundException as e:
            raise Exception(f"Resource not found: {e.message}") from e
        except InvalidAmountException as e:
            raise Exception(f"Failed to send invitation: {e.message}") from e
        except DomainException as e:
            raise Exception(f"Domain error: {e.message}") from e

    @strawberry.mutation
    def create_withdrawal_request(
        self,
        info: Info,
        account_id: str,
        amount: int,
        description: str | None = None,
    ) -> WithdrawalRequest:
        """出金リクエストを作成（子が発行）"""
        withdrawal_request_service = info.context["withdrawal_request_service"]
        try:
            return resolvers.create_withdrawal_request(
                account_id, amount, withdrawal_request_service, description
            )
        except ResourceNotFoundException as e:
            raise Exception(f"Resource not found: {e.message}") from e
        except InvalidAmountException as e:
            raise Exception(f"Invalid amount: {e.message}") from e
        except DomainException as e:
            raise Exception(f"Domain error: {e.message}") from e

    @strawberry.mutation
    def approve_withdrawal_request(
        self,
        info: Info,
        request_id: str,
    ) -> WithdrawalRequest:
        """出金リクエストを承認（親が承認）"""
        withdrawal_request_service = info.context["withdrawal_request_service"]
        transaction_service = info.context["transaction_service"]
        try:
            return resolvers.approve_withdrawal_request(
                request_id, withdrawal_request_service, transaction_service
            )
        except ResourceNotFoundException as e:
            raise Exception(f"Resource not found: {e.message}") from e
        except InvalidAmountException as e:
            raise Exception(f"Invalid operation: {e.message}") from e
        except DomainException as e:
            raise Exception(f"Domain error: {e.message}") from e

    @strawberry.mutation
    def reject_withdrawal_request(
        self,
        info: Info,
        request_id: str,
    ) -> WithdrawalRequest:
        """出金リクエストを却下（親が却下）"""
        withdrawal_request_service = info.context["withdrawal_request_service"]
        try:
            return resolvers.reject_withdrawal_request(request_id, withdrawal_request_service)
        except ResourceNotFoundException as e:
            raise Exception(f"Resource not found: {e.message}") from e
        except InvalidAmountException as e:
            raise Exception(f"Invalid operation: {e.message}") from e
        except DomainException as e:
            raise Exception(f"Domain error: {e.message}") from e

    @strawberry.mutation
    def update_goal(
        self,
        info: Info,
        account_id: str,
        goal_name: str | None = None,
        goal_amount: int | None = None,
    ) -> Account:
        """アカウントの貯金目標を更新"""
        account_service = info.context["account_service"]
        try:
            return resolvers.update_goal(account_id, goal_name, goal_amount, account_service)
        except ResourceNotFoundException as e:
            raise Exception(f"Resource not found: {e.message}") from e
        except InvalidAmountException as e:
            raise Exception(f"Invalid amount: {e.message}") from e
        except DomainException as e:
            raise Exception(f"Domain error: {e.message}") from e

    @strawberry.mutation
    def update_profile(
        self,
        info: Info,
        user_id: str,
        current_user_id: str,
        name: str | None = None,
        avatar_url: str | None = None,
    ) -> Profile:
        """ユーザープロフィールを更新（本人または親が子を編集可能）"""
        profile_service = info.context["profile_service"]
        try:
            return resolvers.update_profile(
                user_id, current_user_id, name, avatar_url, profile_service
            )
        except ResourceNotFoundException as e:
            raise Exception(f"Resource not found: {e.message}") from e
        except DomainException as e:
            raise Exception(f"Domain error: {e.message}") from e

    @strawberry.mutation
    def delete_child(
        self,
        info: Info,
        parent_id: str,
        child_id: str,
    ) -> bool:
        """子プロフィールを削除（親のみ）"""
        profile_service = info.context["profile_service"]
        try:
            return resolvers.delete_child(parent_id, child_id, profile_service)
        except ResourceNotFoundException as e:
            raise Exception(f"Resource not found: {e.message}") from e
        except InvalidAmountException as e:
            raise Exception(f"Invalid operation: {e.message}") from e
        except DomainException as e:
            raise Exception(f"Domain error: {e.message}") from e

    @strawberry.mutation
    def create_or_update_recurring_deposit(
        self,
        info: Info,
        account_id: str,
        current_user_id: str,
        amount: int,
        day_of_month: int,
        is_active: bool = True,
    ) -> RecurringDeposit:
        """定期入金設定を作成または更新（親のみ）"""
        recurring_deposit_service = info.context["recurring_deposit_service"]
        try:
            return resolvers.create_or_update_recurring_deposit(
                account_id,
                current_user_id,
                amount,
                day_of_month,
                recurring_deposit_service,
                is_active,
            )
        except ResourceNotFoundException as e:
            raise Exception(f"Resource not found: {e.message}") from e
        except InvalidAmountException as e:
            raise Exception(f"Invalid input: {e.message}") from e
        except DomainException as e:
            raise Exception(f"Domain error: {e.message}") from e

    @strawberry.mutation
    def delete_recurring_deposit(
        self,
        info: Info,
        account_id: str,
        current_user_id: str,
    ) -> bool:
        """定期入金設定を削除（親のみ）"""
        recurring_deposit_service = info.context["recurring_deposit_service"]
        try:
            return resolvers.delete_recurring_deposit(
                account_id, current_user_id, recurring_deposit_service
            )
        except ResourceNotFoundException as e:
            raise Exception(f"Resource not found: {e.message}") from e
        except InvalidAmountException as e:
            raise Exception(f"Permission denied: {e.message}") from e
        except DomainException as e:
            raise Exception(f"Domain error: {e.message}") from e

    @strawberry.mutation
    def create_parent_invite(
        self,
        info: Info,
        inviter_id: str,
        email: str,
    ) -> str:
        """親を招待する（トークンを返す）招待者の全ての子どもと受理者が紐づけられる"""
        profile_service = info.context["profile_service"]
        try:
            return resolvers.create_parent_invite(inviter_id, email, profile_service)
        except ResourceNotFoundException as e:
            raise Exception(f"Resource not found: {e.message}") from e
        except InvalidAmountException as e:
            raise Exception(f"Invalid operation: {e.message}") from e
        except DomainException as e:
            raise Exception(f"Domain error: {e.message}") from e

    @strawberry.mutation
    def accept_parent_invite(
        self,
        info: Info,
        token: str,
        current_parent_id: str,
    ) -> bool:
        """親招待を受理して親子関係を作成"""
        profile_service = info.context["profile_service"]
        try:
            return resolvers.accept_parent_invite(token, current_parent_id, profile_service)
        except ResourceNotFoundException as e:
            raise Exception(f"Resource not found: {e.message}") from e
        except InvalidAmountException as e:
            raise Exception(f"Invalid operation: {e.message}") from e
        except DomainException as e:
            raise Exception(f"Domain error: {e.message}") from e


# スキーマの生成
schema = strawberry.Schema(query=Query, mutation=Mutation)

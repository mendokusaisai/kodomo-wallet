"""
StrawberryによるGraphQLスキーマ定義（家族中心モデル）
"""

import strawberry
from strawberry.types import Info

from app.api.graphql import resolvers
from app.api.graphql.types import (
    AccountType,
    FamilyMemberType,
    FamilyType,
    TransactionType,
)
from app.core.exceptions import (
    DomainException,
    InvalidAmountException,
    ResourceNotFoundException,
)


@strawberry.type
class Query:
    """GraphQL クエリ定義（家族中心モデル）"""

    @strawberry.field
    def my_family(self, info: Info) -> FamilyType | None:
        """自分が属する家族（メンバー+口座）を取得"""
        current_uid: str | None = info.context.get("current_uid")
        if not current_uid:
            return None
        family_service = info.context["family_service"]
        try:
            return resolvers.get_my_family(current_uid, family_service)
        except (ResourceNotFoundException, DomainException):
            return None

    @strawberry.field
    def family_accounts(self, info: Info, family_id: str) -> list[AccountType]:
        """家族の口座一覧を取得"""
        account_service = info.context["account_service"]
        try:
            return resolvers.get_family_accounts(family_id, account_service)
        except ResourceNotFoundException as e:
            raise Exception(f"Resource not found: {e.message}") from e
        except DomainException as e:
            raise Exception(f"Domain error: {e.message}") from e

    @strawberry.field
    def account_transactions(
        self,
        info: Info,
        family_id: str,
        account_id: str,
        limit: int = 50,
    ) -> list[TransactionType]:
        """口座のトランザクション一覧を取得"""
        transaction_service = info.context["transaction_service"]
        try:
            return resolvers.get_account_transactions(
                family_id, account_id, transaction_service, limit
            )
        except ResourceNotFoundException as e:
            raise Exception(f"Resource not found: {e.message}") from e
        except DomainException as e:
            raise Exception(f"Domain error: {e.message}") from e



@strawberry.type
class Mutation:
    """GraphQL ミューテーション定義（家族中心モデル）"""

    @strawberry.mutation
    def create_family(
        self,
        info: Info,
        my_name: str,
        email: str,
        family_name: str | None = None,
    ) -> FamilyType:
        """家族を新規作成し呼び出し元を親として追加"""
        current_uid: str | None = info.context.get("current_uid")
        if not current_uid:
            raise Exception("Authentication required")
        family_service = info.context["family_service"]
        try:
            return resolvers.create_family(current_uid, my_name, email, family_service, family_name)
        except (ResourceNotFoundException, InvalidAmountException, DomainException) as e:
            raise Exception(e.message) from e

    @strawberry.mutation
    def invite_parent(
        self,
        info: Info,
        family_id: str,
        email: str,
    ) -> str:
        """親招待トークンを発行"""
        current_uid: str | None = info.context.get("current_uid")
        if not current_uid:
            raise Exception("Authentication required")
        family_service = info.context["family_service"]
        try:
            return resolvers.invite_parent(family_id, current_uid, email, family_service)
        except ResourceNotFoundException as e:
            raise Exception(f"Resource not found: {e.message}") from e
        except DomainException as e:
            raise Exception(f"Domain error: {e.message}") from e

    @strawberry.mutation
    def invite_child(
        self,
        info: Info,
        family_id: str,
        child_name: str,
    ) -> str:
        """子招待トークンを発行（親のみ）"""
        current_uid: str | None = info.context.get("current_uid")
        if not current_uid:
            raise Exception("Authentication required")
        family_service = info.context["family_service"]
        try:
            return resolvers.invite_child(family_id, current_uid, child_name, family_service)
        except InvalidAmountException as e:
            raise Exception(f"Permission denied: {e.message}") from e
        except DomainException as e:
            raise Exception(f"Domain error: {e.message}") from e

    @strawberry.mutation
    def join_as_parent(
        self,
        info: Info,
        token: str,
        name: str,
        email: str,
    ) -> FamilyMemberType:
        """親招待トークンを使って家族に参加"""
        current_uid: str | None = info.context.get("current_uid")
        if not current_uid:
            raise Exception("Authentication required")
        family_service = info.context["family_service"]
        try:
            return resolvers.join_as_parent(token, current_uid, name, email, family_service)
        except ResourceNotFoundException as e:
            raise Exception(f"Resource not found: {e.message}") from e
        except InvalidAmountException as e:
            raise Exception(f"Invalid operation: {e.message}") from e
        except DomainException as e:
            raise Exception(f"Domain error: {e.message}") from e

    @strawberry.mutation
    def join_as_child(
        self,
        info: Info,
        token: str,
    ) -> FamilyMemberType:
        """子招待トークンを使って家族に参加"""
        current_uid: str | None = info.context.get("current_uid")
        if not current_uid:
            raise Exception("Authentication required")
        family_service = info.context["family_service"]
        try:
            return resolvers.join_as_child(token, current_uid, family_service)
        except ResourceNotFoundException as e:
            raise Exception(f"Resource not found: {e.message}") from e
        except InvalidAmountException as e:
            raise Exception(f"Invalid operation: {e.message}") from e
        except DomainException as e:
            raise Exception(f"Domain error: {e.message}") from e

    @strawberry.mutation
    def create_account(
        self,
        info: Info,
        family_id: str,
        name: str,
        currency: str = "JPY",
    ) -> AccountType:
        """口座を新規作成（親のみ）"""
        current_uid: str | None = info.context.get("current_uid")
        if not current_uid:
            raise Exception("Authentication required")
        account_service = info.context["account_service"]
        try:
            return resolvers.create_account(family_id, current_uid, name, account_service, currency)
        except InvalidAmountException as e:
            raise Exception(f"Permission denied: {e.message}") from e
        except DomainException as e:
            raise Exception(f"Domain error: {e.message}") from e

    @strawberry.mutation
    def deposit(
        self,
        info: Info,
        family_id: str,
        account_id: str,
        amount: int,
        note: str | None = None,
    ) -> TransactionType:
        """入金トランザクションを作成（親のみ）"""
        current_uid: str | None = info.context.get("current_uid")
        if not current_uid:
            raise Exception("Authentication required")
        transaction_service = info.context["transaction_service"]
        try:
            return resolvers.deposit(
                family_id, account_id, current_uid, amount, transaction_service, note
            )
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
        family_id: str,
        account_id: str,
        amount: int,
        note: str | None = None,
    ) -> TransactionType:
        """出金トランザクションを作成（親のみ）"""
        current_uid: str | None = info.context.get("current_uid")
        if not current_uid:
            raise Exception("Authentication required")
        transaction_service = info.context["transaction_service"]
        try:
            return resolvers.withdraw(
                family_id, account_id, current_uid, amount, transaction_service, note
            )
        except ResourceNotFoundException as e:
            raise Exception(f"Resource not found: {e.message}") from e
        except InvalidAmountException as e:
            raise Exception(f"Invalid amount: {e.message}") from e
        except DomainException as e:
            raise Exception(f"Domain error: {e.message}") from e

    @strawberry.mutation
    def update_goal(
        self,
        info: Info,
        family_id: str,
        account_id: str,
        goal_name: str | None = None,
        goal_amount: int | None = None,
    ) -> AccountType:
        """口座の貯金目標を更新（親のみ）"""
        current_uid: str | None = info.context.get("current_uid")
        if not current_uid:
            raise Exception("Authentication required")
        account_service = info.context["account_service"]
        try:
            return resolvers.update_goal(
                family_id, account_id, current_uid, account_service, goal_name, goal_amount
            )
        except ResourceNotFoundException as e:
            raise Exception(f"Resource not found: {e.message}") from e
        except InvalidAmountException as e:
            raise Exception(f"Invalid amount: {e.message}") from e
        except DomainException as e:
            raise Exception(f"Domain error: {e.message}") from e

# スキーマの生成
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)


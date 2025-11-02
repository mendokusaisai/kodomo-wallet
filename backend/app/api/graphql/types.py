"""
StrawberryのGraphQL型定義
"""

from __future__ import annotations

import strawberry
from strawberry.types import Info

from app.api.graphql import converters


@strawberry.type
class Profile:
    """ユーザープロフィール型"""

    id: str
    name: str
    role: str
    avatar_url: str | None
    created_at: str
    updated_at: str
    auth_user_id: str | None = None  # 認証アカウントID (認証なし子どもの場合None)
    email: str | None = None  # メールアドレス

    # 新フィールド: 複数親のサポート
    @strawberry.field
    def parents(self, info: Info) -> list[Profile]:
        """このプロフィール（子）の親プロフィール一覧を返す"""
        profile_service = info.context.get("profile_service")
        if not profile_service:
            return []
        # FamilyRelationshipRepository から親一覧を取得
        parents = profile_service.family_relationship_repo.get_parents(self.id)
        return [converters.to_graphql_profile(p) for p in parents]


@strawberry.type
class Account:
    """アカウント型"""

    id: str
    user_id: str
    balance: int
    currency: str
    goal_name: str | None
    goal_amount: int | None
    created_at: str
    updated_at: str
    user: Profile | None = None  # アカウント所有者の情報


@strawberry.type
class Transaction:
    """トランザクション型"""

    id: str
    account_id: str
    type: str
    amount: int
    description: str | None
    created_at: str


@strawberry.type
class WithdrawalRequest:
    """Withdrawal request type"""

    id: str
    account_id: str
    amount: int
    description: str | None
    status: str
    created_at: str
    updated_at: str


@strawberry.type
class RecurringDeposit:
    """Recurring deposit type"""

    id: str
    account_id: str
    amount: int
    day_of_month: int
    is_active: bool
    created_at: str
    updated_at: str

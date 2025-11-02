from dataclasses import replace
from datetime import UTC, datetime

from injector import inject

from app.core.exceptions import InvalidAmountException, ResourceNotFoundException
from app.domain.entities import Account
from app.repositories.interfaces import AccountRepository, ProfileRepository


class AccountService:
    """アカウント関連のビジネスロジックサービス"""

    @inject
    def __init__(self, account_repo: AccountRepository, profile_repo: ProfileRepository):
        self.account_repo = account_repo
        self.profile_repo = profile_repo

    def get_user_accounts(self, user_id: str) -> list[Account]:
        """ユーザーの全アカウントを取得"""
        return self.account_repo.get_by_user_id(user_id)

    def get_family_accounts(self, user_id: str) -> list[Account]:
        """ユーザーのアカウントを取得。親の場合は子供のアカウントのみを返す"""
        # ロールを確認するためにユーザープロフィールを取得
        profile = self.profile_repo.get_by_id(user_id)

        if profile and profile.role == "parent":
            # 親は自分のアカウントではなく子供のアカウントのみを見る
            accounts = []
            children = self.profile_repo.get_children(user_id)
            for child in children:
                child_accounts = self.account_repo.get_by_user_id(str(child.id))
                accounts.extend(child_accounts)
        else:
            # 子供は自分のアカウントを見る
            accounts = self.account_repo.get_by_user_id(user_id)

        return accounts

    def update_goal(
        self, account_id: str, goal_name: str | None, goal_amount: int | None
    ) -> Account:
        """アカウントの貯金目標を更新"""
        # アカウントを取得
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ResourceNotFoundException("Account", account_id)

        # 目標金額が指定されている場合は検証
        if goal_amount is not None and goal_amount < 0:
            raise InvalidAmountException(goal_amount, "Goal amount must be non-negative")

        # ドメインエンティティを更新
        updated_account = replace(
            account,
            goal_name=goal_name,
            goal_amount=goal_amount,
            updated_at=datetime.now(UTC),
        )

        # Repositoryを通じて永続化
        return self.account_repo.update(updated_account)

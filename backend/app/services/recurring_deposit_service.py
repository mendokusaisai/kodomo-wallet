from datetime import UTC, datetime

from injector import inject

from app.core.exceptions import InvalidAmountException, ResourceNotFoundException
from app.models.models import RecurringDeposit
from app.repositories.interfaces import (
    AccountRepository,
    ProfileRepository,
    RecurringDepositRepository,
)


class RecurringDepositService:
    """定期入金関連のビジネスロジックサービス"""

    @inject
    def __init__(
        self,
        recurring_deposit_repo: RecurringDepositRepository,
        account_repo: AccountRepository,
        profile_repo: ProfileRepository,
    ):
        self.recurring_deposit_repo = recurring_deposit_repo
        self.account_repo = account_repo
        self.profile_repo = profile_repo

    def get_recurring_deposit(
        self, account_id: str, current_user_id: str
    ) -> RecurringDeposit | None:
        """定期入金設定を取得（親のみ）"""
        # アカウントを取得
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ResourceNotFoundException("Account", account_id)

        # アカウント所有者のプロフィールを取得
        profile = self.profile_repo.get_by_id(str(account.user_id))
        if not profile:
            raise ResourceNotFoundException("Profile", str(account.user_id))

        # 親のみが定期入金設定を閲覧可能
        if str(profile.role) == "parent":
            # 親が自分のアカウントを閲覧（一般的ではないが許可）
            if str(account.user_id) != current_user_id:
                raise InvalidAmountException(0, "You don't have permission to view this")
        elif str(profile.role) == "child":
            # この子供の親である必要がある
            if str(profile.parent_id) != current_user_id:
                raise InvalidAmountException(
                    0, "You can only view recurring deposits for your own children"
                )
        else:
            raise InvalidAmountException(0, "Invalid role")

        return self.recurring_deposit_repo.get_by_account_id(account_id)

    def create_or_update_recurring_deposit(
        self,
        account_id: str,
        current_user_id: str,
        amount: int,
        day_of_month: int,
        is_active: bool = True,
    ) -> RecurringDeposit:
        """定期入金設定を作成または更新（親のみ）"""
        # 金額を検証
        if amount <= 0:
            raise InvalidAmountException(amount, "Amount must be positive")

        # 月の日を検証
        if day_of_month < 1 or day_of_month > 31:
            raise InvalidAmountException(day_of_month, "Day must be between 1 and 31")

        # アカウントを取得
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ResourceNotFoundException("Account", account_id)

        # アカウント所有者のプロフィールを取得
        profile = self.profile_repo.get_by_id(str(account.user_id))
        if not profile:
            raise ResourceNotFoundException("Profile", str(account.user_id))

        # 親のみが定期入金設定を変更可能
        if str(profile.role) == "parent":
            # 親が自分のアカウントを変更（一般的ではないが許可）
            if str(account.user_id) != current_user_id:
                raise InvalidAmountException(0, "You don't have permission to modify this")
        elif str(profile.role) == "child":
            # この子供の親である必要がある
            if str(profile.parent_id) != current_user_id:
                raise InvalidAmountException(
                    0, "You can only modify recurring deposits for your own children"
                )
        else:
            raise InvalidAmountException(0, "Invalid role")

        # 定期入金設定が既に存在するか確認
        existing = self.recurring_deposit_repo.get_by_account_id(account_id)

        now = datetime.now(UTC)

        if existing:
            # 既存を更新
            return self.recurring_deposit_repo.update(
                existing, amount, day_of_month, is_active, now
            )
        else:
            # 新規作成
            return self.recurring_deposit_repo.create(account_id, amount, day_of_month, now)

    def delete_recurring_deposit(self, account_id: str, current_user_id: str) -> bool:
        """定期入金設定を削除（親のみ）"""
        # アカウントを取得
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ResourceNotFoundException("Account", account_id)

        # アカウント所有者のプロフィールを取得
        profile = self.profile_repo.get_by_id(str(account.user_id))
        if not profile:
            raise ResourceNotFoundException("Profile", str(account.user_id))

        # 親のみが定期入金設定を削除可能
        if str(profile.role) == "parent":
            # 親が自分のアカウントを削除（一般的ではないが許可）
            if str(account.user_id) != current_user_id:
                raise InvalidAmountException(0, "You don't have permission to delete this")
        elif str(profile.role) == "child":
            # この子供の親である必要がある
            if str(profile.parent_id) != current_user_id:
                raise InvalidAmountException(
                    0, "You can only delete recurring deposits for your own children"
                )
        else:
            raise InvalidAmountException(0, "Invalid role")

        # 定期入金設定を取得
        recurring_deposit = self.recurring_deposit_repo.get_by_account_id(account_id)
        if not recurring_deposit:
            raise ResourceNotFoundException("RecurringDeposit", account_id)

        return self.recurring_deposit_repo.delete(recurring_deposit)

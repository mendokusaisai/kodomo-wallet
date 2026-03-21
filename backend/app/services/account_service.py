from dataclasses import replace
from datetime import UTC, datetime

from injector import inject

from app.core.exceptions import BusinessRuleViolationException, InvalidAmountException, ResourceNotFoundException
from app.domain.entities import Account
from app.repositories.interfaces import AccountRepository, FamilyMemberRepository


class AccountService:
    """アカウント関連のビジネスロジックサービス（家族中心モデル）"""

    @inject
    def __init__(
        self,
        account_repo: AccountRepository,
        member_repo: FamilyMemberRepository,
    ):
        self.account_repo = account_repo
        self.member_repo = member_repo

    def get_family_accounts(self, family_id: str) -> list[Account]:
        """家族の全口座を取得"""
        return self.account_repo.get_by_family_id(family_id)

    def create_account(
        self,
        family_id: str,
        name: str,
        current_uid: str,
        currency: str = "JPY",
    ) -> Account:
        """口座を新規作成（親のみ）"""
        member = self.member_repo.get_by_uid(family_id, current_uid)
        if not member or member.role != "parent":
            raise BusinessRuleViolationException("parent_only", "Only parents can create accounts")

        return self.account_repo.create(
            family_id=family_id,
            name=name,
            balance=0,
            currency=currency,
        )

    def update_goal(
        self,
        family_id: str,
        account_id: str,
        current_uid: str,
        goal_name: str | None,
        goal_amount: int | None,
    ) -> Account:
        """口座の貯金目標を更新（親のみ）"""
        member = self.member_repo.get_by_uid(family_id, current_uid)
        if not member or member.role != "parent":
            raise BusinessRuleViolationException("parent_only", "Only parents can update account goals")

        account = self.account_repo.get_by_id(family_id, account_id)
        if not account:
            raise ResourceNotFoundException("Account", account_id)

        if goal_amount is not None and goal_amount < 0:
            raise InvalidAmountException(goal_amount, "Goal amount must be non-negative")

        updated_account = replace(
            account,
            goal_name=goal_name,
            goal_amount=goal_amount,
            updated_at=datetime.now(UTC),
        )
        return self.account_repo.update(updated_account)

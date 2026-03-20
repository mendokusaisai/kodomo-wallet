from datetime import UTC, datetime, timedelta

from injector import inject

from app.core.exceptions import InvalidAmountException, ResourceNotFoundException
from app.domain.entities import RecurringDeposit
from app.repositories.interfaces import (
    AccountRepository,
    FamilyMemberRepository,
    RecurringDepositRepository,
    TransactionRepository,
)


class RecurringDepositService:
    """定期入金関連のビジネスロジックサービス（家族中心モデル）"""

    @inject
    def __init__(
        self,
        recurring_deposit_repo: RecurringDepositRepository,
        account_repo: AccountRepository,
        member_repo: FamilyMemberRepository,
        transaction_repo: TransactionRepository,
    ):
        self.recurring_deposit_repo = recurring_deposit_repo
        self.account_repo = account_repo
        self.member_repo = member_repo
        self.transaction_repo = transaction_repo

    def get_recurring_deposit(
        self, family_id: str, account_id: str
    ) -> RecurringDeposit | None:
        """定期入金設定を取得"""
        account = self.account_repo.get_by_id(family_id, account_id)
        if not account:
            raise ResourceNotFoundException("Account", account_id)
        return self.recurring_deposit_repo.get_by_account_id(family_id, account_id)

    def create_or_update_recurring_deposit(
        self,
        family_id: str,
        account_id: str,
        current_uid: str,
        amount: int,
        interval_days: int,
        is_active: bool = True,
    ) -> RecurringDeposit:
        """定期入金設定を作成または更新（親のみ）"""
        if amount <= 0:
            raise InvalidAmountException(amount, "Amount must be positive")
        if interval_days < 1:
            raise InvalidAmountException(interval_days, "Interval must be at least 1 day")

        member = self.member_repo.get_by_uid(family_id, current_uid)
        if not member or member.role != "parent":
            raise InvalidAmountException(0, "Only parents can manage recurring deposits")

        account = self.account_repo.get_by_id(family_id, account_id)
        if not account:
            raise ResourceNotFoundException("Account", account_id)

        now = datetime.now(UTC)
        next_execute_at = now + timedelta(days=interval_days)

        existing = self.recurring_deposit_repo.get_by_account_id(family_id, account_id)
        if existing:
            return self.recurring_deposit_repo.update(
                existing, amount, interval_days, is_active, next_execute_at
            )
        else:
            return self.recurring_deposit_repo.create(
                family_id=family_id,
                account_id=account_id,
                amount=amount,
                interval_days=interval_days,
                next_execute_at=next_execute_at,
                created_by_uid=current_uid,
                created_at=now,
            )

    def delete_recurring_deposit(
        self, family_id: str, account_id: str, current_uid: str
    ) -> bool:
        """定期入金設定を削除（親のみ）"""
        member = self.member_repo.get_by_uid(family_id, current_uid)
        if not member or member.role != "parent":
            raise InvalidAmountException(0, "Only parents can delete recurring deposits")

        recurring_deposit = self.recurring_deposit_repo.get_by_account_id(family_id, account_id)
        if not recurring_deposit:
            raise ResourceNotFoundException("RecurringDeposit", account_id)

        return self.recurring_deposit_repo.delete(recurring_deposit.id)

    def process_due_deposits(self) -> list[str]:
        """実行期限が到来した定期入金を一括実行（バッチ用）"""
        now = datetime.now(UTC)
        due = self.recurring_deposit_repo.get_due(now)
        processed_ids: list[str] = []

        for rd in due:
            account = self.account_repo.get_by_id(rd.family_id, rd.account_id)
            if not account:
                continue

            self.account_repo.update_balance(account, account.balance + rd.amount)
            self.transaction_repo.create(
                family_id=rd.family_id,
                account_id=rd.account_id,
                transaction_type="deposit",
                amount=rd.amount,
                note="定期入金",
                created_by_uid=rd.created_by_uid,
                created_at=now,
            )

            next_execute_at = now + timedelta(days=rd.interval_days)
            self.recurring_deposit_repo.update(
                rd,
                amount=None,
                interval_days=None,
                is_active=None,
                next_execute_at=next_execute_at,
            )
            processed_ids.append(rd.id)

        return processed_ids

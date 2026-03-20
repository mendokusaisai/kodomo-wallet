from datetime import UTC, datetime

from injector import inject

from app.core.exceptions import InvalidAmountException, ResourceNotFoundException
from app.domain.entities import Transaction
from app.repositories.interfaces import (
    AccountRepository,
    FamilyMemberRepository,
    TransactionRepository,
)


class TransactionService:
    """トランザクション関連のビジネスロジックサービス（家族中心モデル）"""

    @inject
    def __init__(
        self,
        transaction_repo: TransactionRepository,
        account_repo: AccountRepository,
        member_repo: FamilyMemberRepository,
    ):
        self.transaction_repo = transaction_repo
        self.account_repo = account_repo
        self.member_repo = member_repo

    def get_account_transactions(
        self, family_id: str, account_id: str, limit: int = 50
    ) -> list[Transaction]:
        """口座のトランザクションを取得"""
        return self.transaction_repo.get_by_account_id(family_id, account_id, limit)

    def create_deposit(
        self,
        family_id: str,
        account_id: str,
        current_uid: str,
        amount: int,
        note: str | None = None,
    ) -> Transaction:
        """入金トランザクションを作成し残高を更新（親のみ）"""
        if amount <= 0:
            raise InvalidAmountException(amount, "Amount must be greater than zero")

        member = self.member_repo.get_by_uid(family_id, current_uid)
        if not member or member.role != "parent":
            raise InvalidAmountException(0, "Only parents can create deposits")

        account = self.account_repo.get_by_id(family_id, account_id)
        if not account:
            raise ResourceNotFoundException("Account", account_id)

        self.account_repo.update_balance(account, account.balance + amount)

        return self.transaction_repo.create(
            family_id=family_id,
            account_id=account_id,
            transaction_type="deposit",
            amount=amount,
            note=note,
            created_by_uid=current_uid,
            created_at=datetime.now(UTC),
        )

    def create_withdraw(
        self,
        family_id: str,
        account_id: str,
        current_uid: str,
        amount: int,
        note: str | None = None,
    ) -> Transaction:
        """出金トランザクションを作成し残高を更新（親のみ）"""
        if amount <= 0:
            raise InvalidAmountException(amount, "Amount must be greater than zero")

        member = self.member_repo.get_by_uid(family_id, current_uid)
        if not member or member.role != "parent":
            raise InvalidAmountException(0, "Only parents can create withdrawals")

        account = self.account_repo.get_by_id(family_id, account_id)
        if not account:
            raise ResourceNotFoundException("Account", account_id)

        if account.balance < amount:
            raise InvalidAmountException(
                amount,
                f"Insufficient balance. Current: {account.balance}, Required: {amount}",
            )

        self.account_repo.update_balance(account, account.balance - amount)

        return self.transaction_repo.create(
            family_id=family_id,
            account_id=account_id,
            transaction_type="withdraw",
            amount=amount,
            note=note,
            created_by_uid=current_uid,
            created_at=datetime.now(UTC),
        )

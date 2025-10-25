from datetime import UTC, datetime

from injector import inject

from app.core.exceptions import InvalidAmountException, ResourceNotFoundException
from app.models.models import Transaction
from app.repositories.interfaces import AccountRepository, TransactionRepository


class TransactionService:
    """トランザクション関連のビジネスロジックサービス"""

    @inject
    def __init__(
        self,
        transaction_repo: TransactionRepository,
        account_repo: AccountRepository,
    ):
        self.transaction_repo = transaction_repo
        self.account_repo = account_repo

    def get_account_transactions(self, account_id: str, limit: int = 50) -> list[Transaction]:
        """アカウントのトランザクションを取得"""
        return self.transaction_repo.get_by_account_id(account_id, limit)

    def create_deposit(
        self, account_id: str, amount: int, description: str | None = None
    ) -> Transaction:
        """入金トランザクションを作成しアカウント残高を更新"""
        # 金額を検証
        if amount <= 0:
            raise InvalidAmountException(amount, "Amount must be greater than zero")

        # アカウントを取得
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ResourceNotFoundException("Account", account_id)

        # 残高を更新（SQLAlchemy Columnタイプのためtype: ignore）
        new_balance = int(account.balance) + amount  # type: ignore[arg-type]
        self.account_repo.update_balance(account, new_balance)

        # トランザクションを作成
        transaction = self.transaction_repo.create(
            account_id=account_id,
            transaction_type="deposit",
            amount=amount,
            description=description,
            created_at=datetime.now(UTC),
        )

        return transaction

    def create_withdraw(
        self, account_id: str, amount: int, description: str | None = None
    ) -> Transaction:
        """出金トランザクションを作成しアカウント残高を更新"""
        # 金額を検証
        if amount <= 0:
            raise InvalidAmountException(amount, "Amount must be greater than zero")

        # アカウントを取得
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ResourceNotFoundException("Account", account_id)

        # 残高が十分か確認
        current_balance = int(account.balance)  # type: ignore[arg-type]
        if current_balance < amount:
            raise InvalidAmountException(
                amount, f"Insufficient balance. Current: {current_balance}, Required: {amount}"
            )

        # 残高を更新
        new_balance = current_balance - amount
        self.account_repo.update_balance(account, new_balance)

        # トランザクションを作成
        transaction = self.transaction_repo.create(
            account_id=account_id,
            transaction_type="withdraw",
            amount=amount,
            description=description,
            created_at=datetime.now(UTC),
        )

        return transaction

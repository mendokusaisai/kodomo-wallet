"""テスト用のリポジトリのモック実装"""

from datetime import datetime
from uuid import uuid4

from app.models.models import Account, Profile, RecurringDeposit, Transaction, WithdrawalRequest
from app.repositories.interfaces import (
    AccountRepository,
    ProfileRepository,
    RecurringDepositRepository,
    TransactionRepository,
    WithdrawalRequestRepository,
)


class MockProfileRepository(ProfileRepository):
    """テスト用の ProfileRepository のモック実装"""

    def __init__(self):
        self.profiles: dict[str, Profile] = {}

    def get_by_id(self, user_id: str) -> Profile | None:
        """ID でプロフィールを取得"""
        return self.profiles.get(user_id)

    def get_children(self, parent_id: str) -> list[Profile]:
        """親の全ての子プロフィールを取得"""
        return [
            profile
            for profile in self.profiles.values()
            if profile.parent_id and str(profile.parent_id) == parent_id
        ]

    def get_by_auth_user_id(self, auth_user_id: str) -> Profile | None:
        """認証ユーザー ID でプロフィールを取得"""
        for profile in self.profiles.values():
            if profile.auth_user_id and str(profile.auth_user_id) == auth_user_id:
                return profile
        return None

    def get_by_email(self, email: str) -> Profile | None:
        """メールアドレスで未認証プロフィールを取得（auth_user_id が NULL）"""
        for profile in self.profiles.values():
            if profile.email == email and profile.auth_user_id is None:
                return profile
        return None

    def create_child(self, name: str, parent_id: str, email: str | None = None) -> Profile:
        """認証なしで子プロフィールを作成"""
        from uuid import UUID

        profile = Profile(
            id=uuid4(),
            name=name,
            role="child",
            parent_id=UUID(parent_id),
            email=email,
            auth_user_id=None,
            created_at=str(datetime.now()),
            updated_at=str(datetime.now()),
        )
        self.profiles[str(profile.id)] = profile
        return profile

    def link_to_auth(self, profile_id: str, auth_user_id: str) -> Profile:
        """既存プロフィールを認証アカウントに紐付け"""
        from uuid import UUID

        profile = self.profiles.get(profile_id)
        if not profile:
            raise ValueError(f"Profile {profile_id} not found")
        profile.auth_user_id = UUID(auth_user_id)
        profile.updated_at = str(datetime.now())
        return profile

    def delete(self, user_id: str) -> bool:
        """プロフィールを削除"""
        if user_id in self.profiles:
            del self.profiles[user_id]
            return True
        return False

    def add(self, profile: Profile) -> None:
        """テスト用にプロフィールを追加"""
        self.profiles[str(profile.id)] = profile


class MockAccountRepository(AccountRepository):
    """テスト用の AccountRepository のモック実装"""

    def __init__(self):
        self.accounts: dict[str, Account] = {}

    def get_by_user_id(self, user_id: str) -> list[Account]:
        """ユーザーの全アカウントを取得"""
        return [acc for acc in self.accounts.values() if str(acc.user_id) == user_id]

    def get_by_id(self, account_id: str) -> Account | None:
        """ID でアカウントを取得"""
        return self.accounts.get(account_id)

    def update_balance(self, account: Account, new_balance: int) -> None:
        """アカウント残高を更新"""
        account.balance = new_balance

    def create(self, user_id: str, balance: int, currency: str) -> Account:
        """新規アカウントを作成"""
        from uuid import UUID

        account = Account(
            id=uuid4(),
            user_id=UUID(user_id),
            balance=balance,
            currency=currency,
            created_at=str(datetime.now()),
            updated_at=str(datetime.now()),
        )
        self.accounts[str(account.id)] = account
        return account

    def delete(self, account_id: str) -> bool:
        """アカウントを削除"""
        if account_id in self.accounts:
            del self.accounts[account_id]
            return True
        return False

    def add(self, account: Account) -> None:
        """テスト用にアカウントを追加"""
        self.accounts[str(account.id)] = account


class MockTransactionRepository(TransactionRepository):
    """テスト用の TransactionRepository のモック実装"""

    def __init__(self):
        self.transactions: list[Transaction] = []

    def get_by_account_id(self, account_id: str, limit: int = 50) -> list[Transaction]:
        """アカウントのトランザクションを取得"""
        account_transactions = [t for t in self.transactions if str(t.account_id) == account_id]
        # created_at の降順でソート
        account_transactions.sort(key=lambda t: t.created_at, reverse=True)
        return account_transactions[:limit]

    def create(
        self,
        account_id: str,
        transaction_type: str,
        amount: int,
        description: str | None,
        created_at: datetime,
    ) -> Transaction:
        """新規トランザクションを作成"""
        from uuid import UUID

        transaction = Transaction(
            id=uuid4(),
            account_id=UUID(account_id),
            type=transaction_type,
            amount=amount,
            description=description,
            created_at=created_at,
        )
        self.transactions.append(transaction)
        return transaction


class MockWithdrawalRequestRepository(WithdrawalRequestRepository):
    """テスト用の WithdrawalRequestRepository のモック実装"""

    def __init__(self):
        self.requests: dict[str, WithdrawalRequest] = {}

    def get_by_id(self, request_id: str) -> WithdrawalRequest | None:
        """ID で出金リクエストを取得"""
        return self.requests.get(request_id)

    def get_pending_by_parent(self, parent_id: str) -> list[WithdrawalRequest]:
        """親の子供の全ての保留中出金リクエストを取得"""
        # 注: モック実装では parent_id との関連付けは簡略化
        # 実際の実装では Account -> Profile -> parent_id で絞り込む必要がある
        _ = parent_id  # 将来の実装のためにパラメータを保持
        return [req for req in self.requests.values() if req.status == "pending"]

    def create(
        self,
        account_id: str,
        amount: int,
        description: str | None,
        created_at: datetime,
    ) -> WithdrawalRequest:
        """新規出金リクエストを作成"""
        from uuid import UUID

        request = WithdrawalRequest(
            id=uuid4(),
            account_id=UUID(account_id),
            amount=amount,
            description=description,
            status="pending",
            created_at=created_at,
            updated_at=created_at,
        )
        self.requests[str(request.id)] = request
        return request

    def update_status(
        self, request: WithdrawalRequest, status: str, updated_at: datetime
    ) -> WithdrawalRequest:
        """出金リクエストのステータスを更新"""
        request.status = status
        request.updated_at = updated_at
        return request


class MockRecurringDepositRepository(RecurringDepositRepository):
    """テスト用の RecurringDepositRepository のモック実装"""

    def __init__(self):
        self.deposits: dict[str, RecurringDeposit] = {}

    def get_by_account_id(self, account_id: str) -> RecurringDeposit | None:
        """アカウント ID で定期入金設定を取得"""
        return self.deposits.get(account_id)

    def create(
        self,
        account_id: str,
        amount: int,
        day_of_month: int,
        created_at: datetime,
    ) -> RecurringDeposit:
        """新規定期入金設定を作成"""
        from uuid import UUID

        deposit = RecurringDeposit(
            id=uuid4(),
            account_id=UUID(account_id),
            amount=amount,
            day_of_month=day_of_month,
            is_active=True,
            created_at=created_at,
            updated_at=created_at,
        )
        self.deposits[account_id] = deposit
        return deposit

    def update(
        self,
        recurring_deposit: RecurringDeposit,
        amount: int | None,
        day_of_month: int | None,
        is_active: bool | None,
        updated_at: datetime,
    ) -> RecurringDeposit:
        """定期入金設定を更新"""
        if amount is not None:
            recurring_deposit.amount = amount
        if day_of_month is not None:
            recurring_deposit.day_of_month = day_of_month
        if is_active is not None:
            recurring_deposit.is_active = is_active
        recurring_deposit.updated_at = updated_at
        return recurring_deposit

    def delete(self, recurring_deposit: RecurringDeposit) -> bool:
        """定期入金設定を削除"""
        account_id = str(recurring_deposit.account_id)
        if account_id in self.deposits:
            del self.deposits[account_id]
            return True
        return False

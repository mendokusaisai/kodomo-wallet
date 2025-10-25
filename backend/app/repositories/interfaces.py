"""
データアクセスのためのRepositoryインターフェース（抽象基底クラス）
"""

from abc import ABC, abstractmethod
from datetime import datetime

from app.models.models import Account, Profile, RecurringDeposit, Transaction, WithdrawalRequest


class ProfileRepository(ABC):
    """Profileのデータアクセスインターフェース"""

    @abstractmethod
    def get_by_id(self, user_id: str) -> Profile | None:
        """IDでプロフィールを取得"""
        pass

    @abstractmethod
    def get_children(self, parent_id: str) -> list[Profile]:
        """親の全ての子プロフィールを取得"""
        pass

    @abstractmethod
    def get_by_auth_user_id(self, auth_user_id: str) -> Profile | None:
        """認証ユーザーIDでプロフィールを取得"""
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Profile | None:
        """メールアドレスで未認証プロフィールを取得（auth_user_idがNULL）"""
        pass

    @abstractmethod
    def create_child(self, name: str, parent_id: str, email: str | None = None) -> Profile:
        """認証なしで子プロフィールを作成"""
        pass

    @abstractmethod
    def link_to_auth(self, profile_id: str, auth_user_id: str) -> Profile:
        """既存プロフィールを認証アカウントに紐付け"""
        pass

    @abstractmethod
    def delete(self, user_id: str) -> bool:
        """プロフィールを削除"""
        pass


class AccountRepository(ABC):
    """Accountのデータアクセスインターフェース"""

    @abstractmethod
    def get_by_user_id(self, user_id: str) -> list[Account]:
        """ユーザーの全アカウントを取得"""
        pass

    @abstractmethod
    def get_by_id(self, account_id: str) -> Account | None:
        """IDでアカウントを取得"""
        pass

    @abstractmethod
    def update_balance(self, account: Account, new_balance: int) -> None:
        """アカウント残高を更新"""
        pass

    @abstractmethod
    def create(self, user_id: str, balance: int, currency: str) -> Account:
        """新規アカウントを作成"""
        pass

    @abstractmethod
    def delete(self, account_id: str) -> bool:
        """アカウントを削除"""
        pass


class TransactionRepository(ABC):
    """Transactionのデータアクセスインターフェース"""

    @abstractmethod
    def get_by_account_id(self, account_id: str, limit: int = 50) -> list[Transaction]:
        """アカウントのトランザクションを取得"""
        pass

    @abstractmethod
    def create(
        self,
        account_id: str,
        transaction_type: str,
        amount: int,
        description: str | None,
        created_at: datetime,
    ) -> Transaction:
        """新規トランザクションを作成"""
        pass


class WithdrawalRequestRepository(ABC):
    """WithdrawalRequestのデータアクセスインターフェース"""

    @abstractmethod
    def get_by_id(self, request_id: str) -> WithdrawalRequest | None:
        """IDで出金リクエストを取得"""
        pass

    @abstractmethod
    def get_pending_by_parent(self, parent_id: str) -> list[WithdrawalRequest]:
        """親の子供の全ての保留中出金リクエストを取得"""
        pass

    @abstractmethod
    def create(
        self,
        account_id: str,
        amount: int,
        description: str | None,
        created_at: datetime,
    ) -> WithdrawalRequest:
        """新規出金リクエストを作成"""
        pass

    @abstractmethod
    def update_status(
        self, request: WithdrawalRequest, status: str, updated_at: datetime
    ) -> WithdrawalRequest:
        """出金リクエストのステータスを更新"""
        pass


class RecurringDepositRepository(ABC):
    """RecurringDepositのデータアクセスインターフェース"""

    @abstractmethod
    def get_by_account_id(self, account_id: str) -> RecurringDeposit | None:
        """アカウントIDで定期入金設定を取得"""
        pass

    @abstractmethod
    def create(
        self,
        account_id: str,
        amount: int,
        day_of_month: int,
        created_at: datetime,
    ) -> RecurringDeposit:
        """新規定期入金設定を作成"""
        pass

    @abstractmethod
    def update(
        self,
        recurring_deposit: RecurringDeposit,
        amount: int | None,
        day_of_month: int | None,
        is_active: bool | None,
        updated_at: datetime,
    ) -> RecurringDeposit:
        """定期入金設定を更新"""
        pass

    @abstractmethod
    def delete(self, recurring_deposit: RecurringDeposit) -> bool:
        """定期入金設定を削除"""
        pass

"""
データアクセスのためのRepositoryインターフェース（抽象基底クラス）
"""

from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.entities import (
    Account,
    FamilyRelationship,
    ParentInvite,
    Profile,
    RecurringDeposit,
    RecurringDepositExecution,
    Transaction,
    WithdrawalRequest,
)


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
    def create_child(self, name: str, parent_id: str, email: str | None = None) -> Profile:
        """子プロフィールを作成（auth.users経由）"""
        pass

    @abstractmethod
    def link_to_auth(self, profile_id: str, auth_user_id: str) -> Profile:
        """既存プロフィールを認証アカウントに紐付け"""
        pass

    @abstractmethod
    def delete(self, user_id: str) -> bool:
        """プロフィールを削除"""
        pass


class FamilyRelationshipRepository(ABC):
    """FamilyRelationship のデータアクセスインターフェース"""

    @abstractmethod
    def get_parents(self, child_id: str) -> list[Profile]:
        """子どもの全ての親を取得"""
        pass

    @abstractmethod
    def get_children(self, parent_id: str) -> list[Profile]:
        """親の全ての子どもを取得"""
        pass

    @abstractmethod
    def has_relationship(self, parent_id: str, child_id: str) -> bool:
        """親子関係が存在するか確認"""
        pass

    @abstractmethod
    def add_relationship(
        self, parent_id: str, child_id: str, relationship_type: str = "parent"
    ) -> FamilyRelationship:
        """親子関係を追加"""
        pass

    @abstractmethod
    def remove_relationship(self, parent_id: str, child_id: str) -> bool:
        """親子関係を削除"""
        pass

    @abstractmethod
    def get_relationship(self, parent_id: str, child_id: str) -> FamilyRelationship | None:
        """特定の親子関係を取得"""
        pass

    @abstractmethod
    def get_related_parents(self, parent_id: str) -> list[str]:
        """
        指定した親と家族関係にある他の親のIDリストを取得
        同じ子どもを共有している親を返す

        Args:
            parent_id: 基準となる親のID

        Returns:
            家族関係にある他の親のIDリスト

        Example:
            親1と親2が子Aを共有 → get_related_parents(親1) → [親2のID]
        """
        pass

    @abstractmethod
    def create_relationship(self, parent_id: str, child_id: str) -> None:
        """
        親子関係を作成（UNIQUE制約により重複は無視）

        Args:
            parent_id: 親のID
            child_id: 子どものID

        Note:
            既に同じ関係が存在する場合は何もしない（エラーにならない）
        """
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
    def update(self, account: Account) -> Account:
        """アカウントを更新"""
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

    @abstractmethod
    def get_active_by_day_of_month(self, day_of_month: int) -> list[RecurringDeposit]:
        """指定日が実行日で有効な定期入金設定を取得"""
        pass


class RecurringDepositExecutionRepository(ABC):
    """定期入金実行履歴のデータアクセスインターフェース"""

    @abstractmethod
    def create(
        self,
        recurring_deposit_id: str,
        transaction_id: str | None,
        status: str,
        amount: int,
        day_of_month: int,
        error_message: str | None,
        executed_at: datetime,
        created_at: datetime,
    ) -> RecurringDepositExecution:
        """実行履歴を作成"""
        pass

    @abstractmethod
    def has_execution_this_month(self, recurring_deposit_id: str, year: int, month: int) -> bool:
        """指定した年月に成功した実行履歴が存在するかチェック"""
        pass

    @abstractmethod
    def get_by_recurring_deposit_id(
        self, recurring_deposit_id: str, limit: int = 10
    ) -> list[RecurringDepositExecution]:
        """定期入金設定IDで実行履歴を取得（最新順）"""
        pass


class ParentInviteRepository(ABC):
    """親招待のデータアクセスインターフェース"""

    @abstractmethod
    def create(
        self,
        child_id: str,
        inviter_id: str,
        email: str,
        expires_at: datetime,
    ) -> ParentInvite:
        """親招待を作成"""
        pass

    @abstractmethod
    def get_by_token(self, token: str) -> ParentInvite | None:
        """トークンで親招待を取得"""
        pass

    @abstractmethod
    def update_status(self, invite: ParentInvite, status: str) -> ParentInvite:
        """親招待のステータスを更新"""
        pass

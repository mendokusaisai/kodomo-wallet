"""
データアクセスのためのRepositoryインターフェース（抽象基底クラス）

家族中心の Firestore データモデルに対応したインターフェース定義。
"""

from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.entities import (
    Account,
    ChildInvite,
    Family,
    FamilyMember,
    ParentInvite,
    Transaction,
)


class FamilyRepository(ABC):
    """Family のデータアクセスインターフェース"""

    @abstractmethod
    def get_by_id(self, family_id: str) -> Family | None:
        """IDで家族を取得"""
        pass

    @abstractmethod
    def create(self, name: str | None = None) -> Family:
        """家族を作成"""
        pass


class FamilyMemberRepository(ABC):
    """FamilyMember のデータアクセスインターフェース"""

    @abstractmethod
    def get_by_uid(self, family_id: str, uid: str) -> FamilyMember | None:
        """UID で家族メンバーを取得"""
        pass

    @abstractmethod
    def get_by_auth_uid(self, uid: str) -> FamilyMember | None:
        """Auth UID で所属家族メンバー（どの家族でも）を取得"""
        pass

    @abstractmethod
    def list_members(self, family_id: str) -> list[FamilyMember]:
        """家族の全メンバーを取得"""
        pass

    @abstractmethod
    def create(
        self,
        family_id: str,
        uid: str,
        name: str,
        role: str,
        email: str | None = None,
    ) -> FamilyMember:
        """家族メンバーを追加"""
        pass

    @abstractmethod
    def update(self, member: FamilyMember) -> FamilyMember:
        """メンバー情報を更新"""
        pass

    @abstractmethod
    def delete(self, family_id: str, uid: str) -> bool:
        """メンバーを削除"""
        pass


class AccountRepository(ABC):
    """Account のデータアクセスインターフェース"""

    @abstractmethod
    def get_by_family_id(self, family_id: str) -> list[Account]:
        """家族の全口座を取得"""
        pass

    @abstractmethod
    def get_by_id(self, family_id: str, account_id: str) -> Account | None:
        """IDで口座を取得"""
        pass

    @abstractmethod
    def create(
        self,
        family_id: str,
        name: str,
        balance: int = 0,
        currency: str = "JPY",
    ) -> Account:
        """新規口座を作成"""
        pass

    @abstractmethod
    def update(self, account: Account) -> Account:
        """口座情報を更新"""
        pass

    @abstractmethod
    def update_balance(self, account: Account, new_balance: int) -> None:
        """口座残高を更新"""
        pass

    @abstractmethod
    def delete(self, family_id: str, account_id: str) -> bool:
        """口座を削除"""
        pass


class TransactionRepository(ABC):
    """Transaction のデータアクセスインターフェース"""

    @abstractmethod
    def get_by_account_id(
        self, family_id: str, account_id: str, limit: int = 50
    ) -> list[Transaction]:
        """口座のトランザクションを取得"""
        pass

    @abstractmethod
    def create(
        self,
        family_id: str,
        account_id: str,
        transaction_type: str,
        amount: int,
        note: str | None,
        created_by_uid: str,
        created_at: datetime,
    ) -> Transaction:
        """新規トランザクションを作成"""
        pass


class ParentInviteRepository(ABC):
    """ParentInvite のデータアクセスインターフェース"""

    @abstractmethod
    def get_by_token(self, token: str) -> ParentInvite | None:
        """トークンで招待を取得"""
        pass

    @abstractmethod
    def create(
        self,
        token: str,
        family_id: str,
        inviter_uid: str,
        email: str,
        expires_at: datetime,
        created_at: datetime,
    ) -> ParentInvite:
        """親招待を作成"""
        pass

    @abstractmethod
    def mark_accepted(self, token: str, accepted_at: datetime) -> ParentInvite:
        """招待を承認済みにする"""
        pass


class ChildInviteRepository(ABC):
    """ChildInvite のデータアクセスインターフェース"""

    @abstractmethod
    def get_by_token(self, token: str) -> ChildInvite | None:
        """トークンで招待を取得"""
        pass

    @abstractmethod
    def create(
        self,
        token: str,
        family_id: str,
        inviter_uid: str,
        child_name: str,
        expires_at: datetime,
        created_at: datetime,
    ) -> ChildInvite:
        """子招待を作成"""
        pass

    @abstractmethod
    def mark_accepted(self, token: str, accepted_at: datetime) -> ChildInvite:
        """招待を承認済みにする"""
        pass


"""テスト用のリポジトリのモック実装"""

from datetime import datetime
from uuid import uuid4

from app.domain.entities import (
    Account,
    FamilyRelationship,
    ParentInvite,
    Profile,
    RecurringDeposit,
    Transaction,
    WithdrawalRequest,
)
from app.repositories.interfaces import (
    AccountRepository,
    FamilyRelationshipRepository,
    ParentInviteRepository,
    ProfileRepository,
    RecurringDepositRepository,
    TransactionRepository,
    WithdrawalRequestRepository,
)


class MockProfileRepository(ProfileRepository):
    """テスト用の ProfileRepository のモック実装"""

    def __init__(self, relationships: set[tuple[str, str]] | None = None):
        self.profiles: dict[str, Profile] = {}
        # 親子関係を (parent_id, child_id) のタプルで保持
        self.relationships: set[tuple[str, str]] = (
            relationships if relationships is not None else set()
        )

    def get_by_id(self, user_id: str) -> Profile | None:
        """ID でプロフィールを取得"""
        return self.profiles.get(user_id)

    def get_children(self, parent_id: str) -> list[Profile]:
        """親の全ての子プロフィールを取得"""
        child_ids = {child for (parent, child) in self.relationships if parent == parent_id}
        return [p for pid, p in self.profiles.items() if pid in child_ids]

    def get_by_auth_user_id(self, auth_user_id: str) -> Profile | None:
        """認証ユーザー ID でプロフィールを取得"""
        for profile in self.profiles.values():
            if profile.auth_user_id and profile.auth_user_id == auth_user_id:
                return profile
        return None

    def create_child(self, name: str, parent_id: str, email: str | None = None) -> Profile:
        """
        認証なしで子プロフィールを作成
        作成した親および関連する全親との関係を自動作成
        """
        profile = Profile(
            id=str(uuid4()),
            name=name,
            role="child",
            email=email,
            auth_user_id=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            avatar_url=None,
        )
        self.profiles[profile.id] = profile

        # 作成した親との関係を追加
        self.relationships.add((parent_id, profile.id))

        # 同じ家族の他の親との関係も作成
        related_parents = self._get_related_parents(parent_id)
        for other_parent_id in related_parents:
            self.relationships.add((other_parent_id, profile.id))

        return profile

    def _get_related_parents(self, parent_id: str) -> list[str]:
        """指定した親と同じ子を持つ他の親を取得"""
        # parent_id が持つ全子どもを取得
        children = {child for (parent, child) in self.relationships if parent == parent_id}

        if not children:
            return []

        # それらの子どもを持つ他の親を取得
        related_parents = set()
        for parent, child in self.relationships:
            if child in children and parent != parent_id:
                related_parents.add(parent)

        return list(related_parents)

    def link_to_auth(self, profile_id: str, auth_user_id: str) -> Profile:
        """既存プロフィールを認証アカウントに紐付け"""
        profile = self.profiles.get(profile_id)
        if not profile:
            raise ValueError(f"Profile {profile_id} not found")
        # dataclassは不変ではないので直接書き換えは不可。新しいインスタンスを作成
        from dataclasses import replace

        updated_profile = replace(profile, auth_user_id=auth_user_id, updated_at=datetime.now())
        self.profiles[profile_id] = updated_profile
        return updated_profile

    def delete(self, user_id: str) -> bool:
        """プロフィールを削除"""
        if user_id in self.profiles:
            del self.profiles[user_id]
            return True
        return False

    def add(self, profile: Profile) -> None:
        """テスト用にプロフィールを追加"""
        self.profiles[str(profile.id)] = profile

    # テスト支援: 親子関係の追加/削除
    def add_relationship(self, parent_id: str, child_id: str) -> None:
        self.relationships.add((parent_id, child_id))

    def remove_relationship(self, parent_id: str, child_id: str) -> None:
        self.relationships.discard((parent_id, child_id))


class MockAccountRepository(AccountRepository):
    """テスト用の AccountRepository のモック実装"""

    def __init__(self):
        self.accounts: dict[str, Account] = {}

    def get_by_user_id(self, user_id: str) -> list[Account]:
        """ユーザーの全アカウントを取得"""
        return [acc for acc in self.accounts.values() if acc.user_id == user_id]

    def get_by_id(self, account_id: str) -> Account | None:
        """ID でアカウントを取得"""
        return self.accounts.get(account_id)

    def update_balance(self, account: Account, new_balance: int) -> None:
        """アカウント残高を更新"""
        from dataclasses import replace

        updated_account = replace(account, balance=new_balance, updated_at=datetime.now())
        self.accounts[account.id] = updated_account

    def update(self, account: Account) -> Account:
        """アカウントを更新"""
        self.accounts[account.id] = account
        return account

    def create(self, user_id: str, balance: int, currency: str) -> Account:
        """新規アカウントを作成"""
        account = Account(
            id=str(uuid4()),
            user_id=user_id,
            balance=balance,
            currency=currency,
            goal_name=None,
            goal_amount=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.accounts[account.id] = account
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
        account_transactions = [t for t in self.transactions if t.account_id == account_id]
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
        transaction = Transaction(
            id=str(uuid4()),
            account_id=account_id,
            type=transaction_type,  # type: ignore
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
        request = WithdrawalRequest(
            id=str(uuid4()),
            account_id=account_id,
            amount=amount,
            description=description,
            status="pending",
            created_at=created_at,
            updated_at=created_at,
        )
        self.requests[request.id] = request
        return request

    def update_status(
        self, request: WithdrawalRequest, status: str, updated_at: datetime
    ) -> WithdrawalRequest:
        """出金リクエストのステータスを更新"""
        from dataclasses import replace

        updated_request = replace(
            request,
            status=status,  # type: ignore
            updated_at=updated_at,
        )
        self.requests[request.id] = updated_request
        return updated_request


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
        deposit = RecurringDeposit(
            id=str(uuid4()),
            account_id=account_id,
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
        from dataclasses import replace

        updates: dict = {"updated_at": updated_at}
        if amount is not None:
            updates["amount"] = amount
        if day_of_month is not None:
            updates["day_of_month"] = day_of_month
        if is_active is not None:
            updates["is_active"] = is_active
        updated_deposit = replace(recurring_deposit, **updates)
        self.deposits[recurring_deposit.account_id] = updated_deposit
        return updated_deposit

    def delete(self, recurring_deposit: RecurringDeposit) -> bool:
        """定期入金設定を削除"""
        account_id = recurring_deposit.account_id
        if account_id in self.deposits:
            del self.deposits[account_id]
            return True
        return False


class MockFamilyRelationshipRepository(FamilyRelationshipRepository):
    """テスト用の FamilyRelationshipRepository のモック実装"""

    def __init__(
        self,
        relationships: set[tuple[str, str]] | None = None,
        profiles: dict[str, Profile] | None = None,
    ):
        # 親子関係 (parent_id, child_id)
        self.relationships: set[tuple[str, str]] = (
            relationships if relationships is not None else set()
        )
        # プロフィール参照（親/子の取得に使用）
        self.profiles = profiles if profiles is not None else {}

    def get_parents(self, child_id: str) -> list[Profile]:
        parent_ids = {parent for (parent, child) in self.relationships if child == child_id}
        return [p for pid, p in self.profiles.items() if pid in parent_ids]

    def get_children(self, parent_id: str) -> list[Profile]:
        child_ids = {child for (parent, child) in self.relationships if parent == parent_id}
        return [p for pid, p in self.profiles.items() if pid in child_ids]

    def has_relationship(self, parent_id: str, child_id: str) -> bool:
        return (parent_id, child_id) in self.relationships

    def add_relationship(
        self, parent_id: str, child_id: str, relationship_type: str = "parent"
    ) -> FamilyRelationship:
        # relationship_type はモックでは未使用
        self.relationships.add((parent_id, child_id))
        return FamilyRelationship(
            id=str(uuid4()),
            parent_id=parent_id,
            child_id=child_id,
            relationship_type="parent",
            created_at=datetime.now(),
        )

    def remove_relationship(self, parent_id: str, child_id: str) -> bool:
        if (parent_id, child_id) in self.relationships:
            self.relationships.remove((parent_id, child_id))
            return True
        return False

    def get_relationship(self, parent_id: str, child_id: str) -> FamilyRelationship | None:
        if (parent_id, child_id) in self.relationships:
            return FamilyRelationship(
                id=str(uuid4()),
                parent_id=parent_id,
                child_id=child_id,
                relationship_type="parent",
                created_at=datetime.now(),
            )
        return None

    def get_related_parents(self, parent_id: str) -> list[str]:
        """指定した親と同じ子を持つ他の親のIDリストを取得"""
        # parent_id が持つ全子どもを取得
        children = {child for (parent, child) in self.relationships if parent == parent_id}

        if not children:
            return []

        # それらの子どもを持つ他の親を取得
        related_parents = set()
        for parent, child in self.relationships:
            if child in children and parent != parent_id:
                related_parents.add(parent)

        return list(related_parents)

    def create_relationship(self, parent_id: str, child_id: str) -> None:
        """親子関係を作成(重複は無視)"""
        # 既に存在していても何もしない(重複を無視)
        self.relationships.add((parent_id, child_id))


class MockParentInviteRepository(ParentInviteRepository):
    """テスト用の ParentInviteRepository のモック実装"""

    def __init__(self):
        # token をキーに保持
        self.invites: dict[str, ParentInvite] = {}

    def create(
        self,
        child_id: str,
        inviter_id: str,
        email: str,
        expires_at: datetime,
    ) -> ParentInvite:
        token = str(uuid4())
        invite = ParentInvite(
            id=str(uuid4()),
            token=token,
            child_id=child_id,
            inviter_id=inviter_id,
            email=email,
            status="pending",
            expires_at=expires_at,
            created_at=datetime.now(),
        )
        self.invites[token] = invite
        return invite

    def get_by_token(self, token: str) -> ParentInvite | None:
        return self.invites.get(token)

    def update_status(self, invite: ParentInvite, status: str) -> ParentInvite:
        from dataclasses import replace

        updated = replace(invite, status=status)
        self.invites[invite.token] = updated
        return updated

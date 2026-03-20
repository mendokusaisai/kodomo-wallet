"""テスト用のリポジトリのモック実装（家族中心モデル対応）"""

from dataclasses import replace
from datetime import datetime
from uuid import uuid4

from app.domain.entities import (
    Account,
    ChildInvite,
    Family,
    FamilyMember,
    ParentInvite,
    Transaction,
)
from app.repositories.interfaces import (
    AccountRepository,
    ChildInviteRepository,
    FamilyMemberRepository,
    FamilyRepository,
    ParentInviteRepository,
    TransactionRepository,
)


class MockFamilyRepository(FamilyRepository):
    """テスト用の FamilyRepository のモック実装"""

    def __init__(self):
        self.families: dict[str, Family] = {}

    def get_by_id(self, family_id: str) -> Family | None:
        return self.families.get(family_id)

    def create(self, name: str | None = None) -> Family:
        family = Family(
            id=str(uuid4()),
            name=name,
            created_at=datetime.now(),
        )
        self.families[family.id] = family
        return family

    def add(self, family: Family) -> None:
        self.families[family.id] = family


class MockFamilyMemberRepository(FamilyMemberRepository):
    """テスト用の FamilyMemberRepository のモック実装"""

    def __init__(self):
        # (family_id, uid) → FamilyMember
        self.members: dict[tuple[str, str], FamilyMember] = {}

    def get_by_uid(self, family_id: str, uid: str) -> FamilyMember | None:
        return self.members.get((family_id, uid))

    def get_by_auth_uid(self, uid: str) -> FamilyMember | None:
        for member in self.members.values():
            if member.uid == uid:
                return member
        return None

    def list_members(self, family_id: str) -> list[FamilyMember]:
        return [m for (fid, _), m in self.members.items() if fid == family_id]

    def create(
        self,
        family_id: str,
        uid: str,
        name: str,
        role: str,
        email: str | None = None,
    ) -> FamilyMember:
        member = FamilyMember(
            uid=uid,
            family_id=family_id,
            name=name,
            role=role,  # type: ignore
            email=email,
            joined_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.members[(family_id, uid)] = member
        return member

    def update(self, member: FamilyMember) -> FamilyMember:
        self.members[(member.family_id, member.uid)] = member
        return member

    def delete(self, family_id: str, uid: str) -> bool:
        key = (family_id, uid)
        if key in self.members:
            del self.members[key]
            return True
        return False

    def add(self, member: FamilyMember) -> None:
        self.members[(member.family_id, member.uid)] = member


class MockAccountRepository(AccountRepository):
    """テスト用の AccountRepository のモック実装"""

    def __init__(self):
        self.accounts: dict[str, Account] = {}

    def get_by_family_id(self, family_id: str) -> list[Account]:
        return [a for a in self.accounts.values() if a.family_id == family_id]

    def get_by_id(self, family_id: str, account_id: str) -> Account | None:
        account = self.accounts.get(account_id)
        if account and account.family_id == family_id:
            return account
        return None

    def create(
        self,
        family_id: str,
        name: str,
        balance: int = 0,
        currency: str = "JPY",
    ) -> Account:
        account = Account(
            id=str(uuid4()),
            family_id=family_id,
            name=name,
            balance=balance,
            currency=currency,
            goal_name=None,
            goal_amount=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.accounts[account.id] = account
        return account

    def update(self, account: Account) -> Account:
        self.accounts[account.id] = account
        return account

    def update_balance(self, account: Account, new_balance: int) -> None:
        updated = replace(account, balance=new_balance, updated_at=datetime.now())
        self.accounts[account.id] = updated

    def delete(self, family_id: str, account_id: str) -> bool:
        if account_id in self.accounts:
            del self.accounts[account_id]
            return True
        return False

    def add(self, account: Account) -> None:
        self.accounts[account.id] = account


class MockTransactionRepository(TransactionRepository):
    """テスト用の TransactionRepository のモック実装"""

    def __init__(self):
        self.transactions: list[Transaction] = []

    def get_by_account_id(
        self, family_id: str, account_id: str, limit: int = 50
    ) -> list[Transaction]:
        txs = [
            t for t in self.transactions
            if t.account_id == account_id and t.family_id == family_id
        ]
        txs.sort(key=lambda t: t.created_at, reverse=True)
        return txs[:limit]

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
        transaction = Transaction(
            id=str(uuid4()),
            account_id=account_id,
            family_id=family_id,
            type=transaction_type,  # type: ignore
            amount=amount,
            note=note,
            created_at=created_at,
            created_by_uid=created_by_uid,
        )
        self.transactions.append(transaction)
        return transaction


class MockParentInviteRepository(ParentInviteRepository):
    """テスト用の ParentInviteRepository のモック実装"""

    def __init__(self):
        self.invites: dict[str, ParentInvite] = {}

    def get_by_token(self, token: str) -> ParentInvite | None:
        return self.invites.get(token)

    def create(
        self,
        token: str,
        family_id: str,
        inviter_uid: str,
        email: str,
        expires_at: datetime,
        created_at: datetime,
    ) -> ParentInvite:
        invite = ParentInvite(
            token=token,
            family_id=family_id,
            inviter_uid=inviter_uid,
            email=email,
            expires_at=expires_at,
            accepted_at=None,
            created_at=created_at,
        )
        self.invites[token] = invite
        return invite

    def mark_accepted(self, token: str, accepted_at: datetime) -> ParentInvite:
        invite = self.invites[token]
        updated = replace(invite, accepted_at=accepted_at)
        self.invites[token] = updated
        return updated


class MockChildInviteRepository(ChildInviteRepository):
    """テスト用の ChildInviteRepository のモック実装"""

    def __init__(self):
        self.invites: dict[str, ChildInvite] = {}

    def get_by_token(self, token: str) -> ChildInvite | None:
        return self.invites.get(token)

    def create(
        self,
        token: str,
        family_id: str,
        inviter_uid: str,
        child_name: str,
        expires_at: datetime,
        created_at: datetime,
    ) -> ChildInvite:
        invite = ChildInvite(
            token=token,
            family_id=family_id,
            inviter_uid=inviter_uid,
            child_name=child_name,
            expires_at=expires_at,
            accepted_at=None,
            created_at=created_at,
        )
        self.invites[token] = invite
        return invite

    def mark_accepted(self, token: str, accepted_at: datetime) -> ChildInvite:
        invite = self.invites[token]
        updated = replace(invite, accepted_at=accepted_at)
        self.invites[token] = updated
        return updated


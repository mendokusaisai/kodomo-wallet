"""サービステスト共通のfixture定義"""

from datetime import UTC, datetime

import pytest
from injector import Binder, Injector, Module

from app.domain.entities import Account, Family, FamilyMember
from app.repositories.interfaces import (
    AccountRepository,
    ChildInviteRepository,
    FamilyMemberRepository,
    FamilyRepository,
    ParentInviteRepository,
    RecurringDepositRepository,
    TransactionRepository,
)
from app.repositories.mock_repositories import (
    MockAccountRepository,
    MockChildInviteRepository,
    MockFamilyMemberRepository,
    MockFamilyRepository,
    MockParentInviteRepository,
    MockRecurringDepositRepository,
    MockTransactionRepository,
)
from app.services.mailer import ConsoleMailer, Mailer

FAMILY_ID = "test-family-id"
PARENT_UID = "test-parent-uid"
CHILD_UID = "test-child-uid"


class RepositoryModule(Module):
    """テスト用のモックリポジトリを提供するモジュール"""

    def __init__(
        self,
        family_repo: MockFamilyRepository,
        member_repo: MockFamilyMemberRepository,
        account_repo: MockAccountRepository,
        transaction_repo: MockTransactionRepository,
        recurring_deposit_repo: MockRecurringDepositRepository | None = None,
        parent_invite_repo: MockParentInviteRepository | None = None,
        child_invite_repo: MockChildInviteRepository | None = None,
    ):
        self.family_repo = family_repo
        self.member_repo = member_repo
        self.account_repo = account_repo
        self.transaction_repo = transaction_repo
        self.recurring_deposit_repo = recurring_deposit_repo or MockRecurringDepositRepository()
        self.parent_invite_repo = parent_invite_repo or MockParentInviteRepository()
        self.child_invite_repo = child_invite_repo or MockChildInviteRepository()

    def configure(self, binder: Binder) -> None:
        binder.bind(FamilyRepository, to=self.family_repo)
        binder.bind(FamilyMemberRepository, to=self.member_repo)
        binder.bind(AccountRepository, to=self.account_repo)
        binder.bind(TransactionRepository, to=self.transaction_repo)
        binder.bind(RecurringDepositRepository, to=self.recurring_deposit_repo)
        binder.bind(ParentInviteRepository, to=self.parent_invite_repo)
        binder.bind(ChildInviteRepository, to=self.child_invite_repo)
        binder.bind(Mailer, to=ConsoleMailer())


@pytest.fixture
def mock_family_repository() -> MockFamilyRepository:
    repo = MockFamilyRepository()
    repo.add(Family(id=FAMILY_ID, name="Test Family", created_at=datetime.now(UTC)))
    return repo


@pytest.fixture
def mock_member_repository() -> MockFamilyMemberRepository:
    repo = MockFamilyMemberRepository()
    repo.add(
        FamilyMember(
            uid=PARENT_UID,
            family_id=FAMILY_ID,
            name="Test Parent",
            role="parent",
            email="parent@example.com",
            joined_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
    )
    repo.add(
        FamilyMember(
            uid=CHILD_UID,
            family_id=FAMILY_ID,
            name="Test Child",
            role="child",
            email=None,
            joined_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
    )
    return repo


@pytest.fixture
def mock_account_repository() -> MockAccountRepository:
    return MockAccountRepository()


@pytest.fixture
def mock_transaction_repository() -> MockTransactionRepository:
    return MockTransactionRepository()


@pytest.fixture
def mock_recurring_deposit_repository() -> MockRecurringDepositRepository:
    return MockRecurringDepositRepository()


@pytest.fixture
def sample_account(mock_account_repository: MockAccountRepository) -> Account:
    account = Account(
        id="sample-account-id",
        family_id=FAMILY_ID,
        name="Test Account",
        balance=10000,
        currency="JPY",
        goal_name=None,
        goal_amount=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    mock_account_repository.add(account)
    return account


@pytest.fixture
def mock_parent_invite_repository() -> MockParentInviteRepository:
    return MockParentInviteRepository()


@pytest.fixture
def mock_child_invite_repository() -> MockChildInviteRepository:
    return MockChildInviteRepository()


@pytest.fixture
def injector_with_mocks(
    mock_family_repository: MockFamilyRepository,
    mock_member_repository: MockFamilyMemberRepository,
    mock_account_repository: MockAccountRepository,
    mock_transaction_repository: MockTransactionRepository,
    mock_recurring_deposit_repository: MockRecurringDepositRepository,
    mock_parent_invite_repository: MockParentInviteRepository,
    mock_child_invite_repository: MockChildInviteRepository,
) -> Injector:
    module = RepositoryModule(
        family_repo=mock_family_repository,
        member_repo=mock_member_repository,
        account_repo=mock_account_repository,
        transaction_repo=mock_transaction_repository,
        recurring_deposit_repo=mock_recurring_deposit_repository,
        parent_invite_repo=mock_parent_invite_repository,
        child_invite_repo=mock_child_invite_repository,
    )
    return Injector([module])


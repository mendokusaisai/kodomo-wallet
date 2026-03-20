"""GraphQL test fixtures（Phase 4 で更新予定）"""

import pytest
from injector import Injector

from app.core.container import create_injector
from app.repositories.mock_repositories import (
    MockAccountRepository,
    MockChildInviteRepository,
    MockFamilyMemberRepository,
    MockFamilyRepository,
    MockParentInviteRepository,
    MockRecurringDepositRepository,
    MockTransactionRepository,
)
from app.repositories.interfaces import (
    AccountRepository,
    ChildInviteRepository,
    FamilyMemberRepository,
    FamilyRepository,
    ParentInviteRepository,
    RecurringDepositRepository,
    TransactionRepository,
)
from app.services import AccountService, FamilyService, RecurringDepositService, TransactionService
from app.services.mailer import ConsoleMailer, Mailer
from injector import Binder, Module, singleton


class MockRepositoryModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(FamilyRepository, to=MockFamilyRepository(), scope=singleton)
        binder.bind(FamilyMemberRepository, to=MockFamilyMemberRepository(), scope=singleton)
        binder.bind(AccountRepository, to=MockAccountRepository(), scope=singleton)
        binder.bind(TransactionRepository, to=MockTransactionRepository(), scope=singleton)
        binder.bind(RecurringDepositRepository, to=MockRecurringDepositRepository(), scope=singleton)
        binder.bind(ParentInviteRepository, to=MockParentInviteRepository(), scope=singleton)
        binder.bind(ChildInviteRepository, to=MockChildInviteRepository(), scope=singleton)
        binder.bind(Mailer, to=ConsoleMailer(), scope=singleton)


@pytest.fixture
def test_injector() -> Injector:
    """テスト用の依存性注入コンテナを作成"""
    return Injector([MockRepositoryModule()])


@pytest.fixture
def graphql_context(test_injector: Injector) -> dict:
    """GraphQL コンテキストを作成"""
    return {
        "family_service": test_injector.get(FamilyService),
        "account_service": test_injector.get(AccountService),
        "transaction_service": test_injector.get(TransactionService),
        "recurring_deposit_service": test_injector.get(RecurringDepositService),
    }


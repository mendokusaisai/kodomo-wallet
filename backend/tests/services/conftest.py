"""サービステスト共通のfixture定義"""

from datetime import UTC, datetime

import pytest
from injector import Binder, Injector, Module

from app.domain.entities import Account, Profile
from app.repositories.interfaces import (
    AccountRepository,
    ProfileRepository,
    RecurringDepositRepository,
    TransactionRepository,
    WithdrawalRequestRepository,
)
from app.repositories.mock_repositories import (
    MockAccountRepository,
    MockProfileRepository,
    MockRecurringDepositRepository,
    MockTransactionRepository,
    MockWithdrawalRequestRepository,
)


class RepositoryModule(Module):
    """テスト用のモックリポジトリを提供するモジュール"""

    def __init__(
        self,
        profile_repo: MockProfileRepository,
        account_repo: MockAccountRepository,
        transaction_repo: MockTransactionRepository,
        withdrawal_request_repo: MockWithdrawalRequestRepository | None = None,
        recurring_deposit_repo: MockRecurringDepositRepository | None = None,
    ):
        self.profile_repo = profile_repo
        self.account_repo = account_repo
        self.transaction_repo = transaction_repo
        self.withdrawal_request_repo = withdrawal_request_repo or MockWithdrawalRequestRepository()
        self.recurring_deposit_repo = recurring_deposit_repo or MockRecurringDepositRepository()

    def configure(self, binder: Binder) -> None:
        """モックリポジトリをバインド"""
        binder.bind(ProfileRepository, to=self.profile_repo)
        binder.bind(AccountRepository, to=self.account_repo)
        binder.bind(TransactionRepository, to=self.transaction_repo)
        binder.bind(WithdrawalRequestRepository, to=self.withdrawal_request_repo)
        binder.bind(RecurringDepositRepository, to=self.recurring_deposit_repo)


@pytest.fixture
def sample_profile() -> Profile:
    """サンプルプロフィールを作成"""
    return Profile(
        id="sample-id",
        auth_user_id="sample-auth-user-id",
        email="test@example.com",
        name="Test User",
        role="parent",
        parent_id=None,
        avatar_url=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.fixture
def sample_child(sample_profile: Profile) -> Profile:
    """サンプル子プロフィールを作成"""
    return Profile(
        id="sample-child-id",
        auth_user_id=None,
        email=None,
        name="Test Child",
        role="child",
        parent_id=sample_profile.id,
        avatar_url=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.fixture
def sample_account(sample_profile: Profile) -> Account:
    """サンプルアカウントを作成"""
    return Account(
        id="sample-account-id",
        user_id=sample_profile.id,
        balance=10000,
        currency="JPY",
        goal_name=None,
        goal_amount=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.fixture
def mock_profile_repository() -> MockProfileRepository:
    """モックのプロフィールリポジトリを作成"""
    return MockProfileRepository()


@pytest.fixture
def mock_account_repository() -> MockAccountRepository:
    """モックのアカウントリポジトリを作成"""
    return MockAccountRepository()


@pytest.fixture
def mock_transaction_repository() -> MockTransactionRepository:
    """モックのトランザクションリポジトリを作成"""
    return MockTransactionRepository()


@pytest.fixture
def mock_withdrawal_request_repository() -> MockWithdrawalRequestRepository:
    """モックの出金リクエストリポジトリを作成"""
    return MockWithdrawalRequestRepository()


@pytest.fixture
def mock_recurring_deposit_repository() -> MockRecurringDepositRepository:
    """モックの定期入金リポジトリを作成"""
    return MockRecurringDepositRepository()


@pytest.fixture
def injector_with_mocks(
    mock_profile_repository,
    mock_account_repository,
    mock_transaction_repository,
    mock_withdrawal_request_repository,
    mock_recurring_deposit_repository,
) -> Injector:
    """モックリポジトリを持つインジェクターを作成"""
    return Injector(
        [
            RepositoryModule(
                mock_profile_repository,
                mock_account_repository,
                mock_transaction_repository,
                mock_withdrawal_request_repository,
                mock_recurring_deposit_repository,
            )
        ]
    )

"""サービス層ビジネスロジックのユニットテスト

依存性注入によるモックリポジトリを使用して
ProfileService、AccountService、TransactionService をテスト
"""

import uuid
from datetime import UTC, datetime

import pytest
from injector import Binder, Injector, Module

from app.core.exceptions import InvalidAmountException, ResourceNotFoundException
from app.models.models import Account, Profile
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
from app.services import (
    AccountService,
    ProfileService,
    RecurringDepositService,
    TransactionService,
    WithdrawalRequestService,
)

# ============================================================================
# 依存性注入用のテストモジュール
# ============================================================================


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


class ServiceModule(Module):
    """サービスインスタンスを提供するモジュール"""

    def configure(self, binder: Binder) -> None:
        """サービスをバインド"""
        binder.bind(ProfileService, to=ProfileService)
        binder.bind(AccountService, to=AccountService)
        binder.bind(TransactionService, to=TransactionService)
        binder.bind(WithdrawalRequestService, to=WithdrawalRequestService)
        binder.bind(RecurringDepositService, to=RecurringDepositService)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_profile_repository():
    """モックのプロフィールリポジトリを作成"""
    return MockProfileRepository()


@pytest.fixture
def mock_account_repository():
    """モックのアカウントリポジトリを作成"""
    return MockAccountRepository()


@pytest.fixture
def mock_transaction_repository():
    """モックのトランザクションリポジトリを作成"""
    return MockTransactionRepository()


@pytest.fixture
def mock_withdrawal_request_repository():
    """モックの出金リクエストリポジトリを作成"""
    return MockWithdrawalRequestRepository()


@pytest.fixture
def mock_recurring_deposit_repository():
    """モックの定期入金リポジトリを作成"""
    return MockRecurringDepositRepository()


@pytest.fixture
def injector_with_mocks(
    mock_profile_repository,
    mock_account_repository,
    mock_transaction_repository,
    mock_withdrawal_request_repository,
    mock_recurring_deposit_repository,
):
    """モックリポジトリを持つインジェクターを作成"""
    return Injector(
        [
            RepositoryModule(
                mock_profile_repository,
                mock_account_repository,
                mock_transaction_repository,
                mock_withdrawal_request_repository,
                mock_recurring_deposit_repository,
            ),
            ServiceModule(),
        ]
    )


@pytest.fixture
def sample_profile():
    """サンプルプロフィールを作成"""
    return Profile(
        id=uuid.uuid4(),
        name="Test User",
        role="parent",
        created_at=str(datetime.now(UTC)),
        updated_at=str(datetime.now(UTC)),
    )


@pytest.fixture
def sample_child():
    """サンプル子プロフィールを作成"""
    return Profile(
        id=uuid.uuid4(),
        name="Test Child",
        role="child",
        created_at=str(datetime.now(UTC)),
        updated_at=str(datetime.now(UTC)),
    )


@pytest.fixture
def sample_account(sample_profile):
    """サンプルアカウントを作成"""
    return Account(
        id=uuid.uuid4(),
        user_id=sample_profile.id,
        balance=10000,
        currency="JPY",
        created_at=str(datetime.now(UTC)),
        updated_at=str(datetime.now(UTC)),
    )


# ============================================================================
# ProfileService Tests
# ============================================================================


class TestProfileService:
    """ProfileService のテストスイート"""

    def test_get_profile_success(
        self, injector_with_mocks, mock_profile_repository, sample_profile
    ):
        """プロフィール取得の成功をテスト"""
        # Setup: モックリポジトリにプロフィールを追加
        mock_profile_repository.add(sample_profile)

        # Test: サービスを取得してプロフィールを取得
        service = injector_with_mocks.get(ProfileService)
        result = service.get_profile(str(sample_profile.id))

        # Verify
        assert result is not None
        assert result.id == sample_profile.id
        assert result.name == "Test User"
        assert result.role == "parent"

    def test_get_profile_not_found(self, injector_with_mocks):
        """Test retrieving a non-existent profile"""
        service = injector_with_mocks.get(ProfileService)
        result = service.get_profile("non-existent-id")

        assert result is None

    def test_get_profile_uses_repository(
        self,
        mock_profile_repository,
        mock_account_repository,
        mock_transaction_repository,
        sample_profile,
    ):
        """Test that ProfileService uses the injected repository"""
        # Setup: Create service with specific repository
        mock_profile_repository.add(sample_profile)

        injector = Injector(
            [
                RepositoryModule(
                    mock_profile_repository,
                    mock_account_repository,
                    mock_transaction_repository,
                ),
                ServiceModule(),
            ]
        )

        service = injector.get(ProfileService)

        # Test
        result = service.get_profile(str(sample_profile.id))

        # Verify that it's the same repository instance
        assert result is not None
        assert result == sample_profile


# ============================================================================
# AccountService Tests
# ============================================================================


class TestAccountService:
    """Test suite for AccountService"""

    def test_get_user_accounts_success(
        self, injector_with_mocks, mock_account_repository, sample_profile
    ):
        """Test successfully retrieving user accounts"""
        # Setup: Add accounts to mock repository
        account1 = Account(
            id=uuid.uuid4(),
            user_id=sample_profile.id,
            balance=5000,
            currency="JPY",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        account2 = Account(
            id=uuid.uuid4(),
            user_id=sample_profile.id,
            balance=3000,
            currency="JPY",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        mock_account_repository.add(account1)
        mock_account_repository.add(account2)

        # Test: Get service and retrieve accounts
        service = injector_with_mocks.get(AccountService)
        results = service.get_user_accounts(str(sample_profile.id))

        # Verify
        assert len(results) == 2
        assert all(str(acc.user_id) == str(sample_profile.id) for acc in results)

    def test_get_user_accounts_empty(self, injector_with_mocks):
        """Test retrieving accounts for user with no accounts"""
        service = injector_with_mocks.get(AccountService)
        results = service.get_user_accounts("non-existent-user")

        assert results == []

    def test_get_user_accounts_filters_by_user_id(
        self, injector_with_mocks, mock_account_repository
    ):
        """Test that only accounts for the specified user are returned"""
        # Setup: Add accounts for different users
        user1_id = uuid.uuid4()
        user2_id = uuid.uuid4()

        account1 = Account(
            id=uuid.uuid4(),
            user_id=user1_id,
            balance=1000,
            currency="JPY",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        account2 = Account(
            id=uuid.uuid4(),
            user_id=user2_id,
            balance=2000,
            currency="JPY",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        account3 = Account(
            id=uuid.uuid4(),
            user_id=user1_id,
            balance=3000,
            currency="JPY",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )

        mock_account_repository.add(account1)
        mock_account_repository.add(account2)
        mock_account_repository.add(account3)

        # Test: Get accounts for user1
        service = injector_with_mocks.get(AccountService)
        results = service.get_user_accounts(str(user1_id))

        # Verify: Only user1's accounts are returned
        assert len(results) == 2
        assert all(str(acc.user_id) == str(user1_id) for acc in results)


# ============================================================================
# TransactionService Tests
# ============================================================================


class TestTransactionService:
    """Test suite for TransactionService"""

    def test_get_account_transactions_success(
        self,
        injector_with_mocks,
        mock_account_repository,
        mock_transaction_repository,
        sample_account,
    ):
        """Test successfully retrieving account transactions"""
        # Setup: Add account and transactions
        mock_account_repository.add(sample_account)
        mock_transaction_repository.create(
            account_id=str(sample_account.id),
            transaction_type="deposit",
            amount=1000,
            description="Test 1",
            created_at=str(datetime.now(UTC)),
        )
        mock_transaction_repository.create(
            account_id=str(sample_account.id),
            transaction_type="withdraw",
            amount=500,
            description="Test 2",
            created_at=str(datetime.now(UTC)),
        )

        # Test: Get service and retrieve transactions
        service = injector_with_mocks.get(TransactionService)
        results = service.get_account_transactions(str(sample_account.id))

        # Verify
        assert len(results) == 2

    def test_get_account_transactions_with_limit(
        self,
        injector_with_mocks,
        mock_account_repository,
        mock_transaction_repository,
        sample_account,
    ):
        """Test retrieving transactions with limit"""
        # Setup: Add account and multiple transactions
        mock_account_repository.add(sample_account)
        for i in range(5):
            mock_transaction_repository.create(
                account_id=str(sample_account.id),
                transaction_type="deposit",
                amount=1000 * (i + 1),
                description=f"Transaction {i + 1}",
                created_at=str(datetime.now(UTC)),
            )

        # Test: Get service and retrieve transactions with limit
        service = injector_with_mocks.get(TransactionService)
        results = service.get_account_transactions(str(sample_account.id), limit=3)

        # Verify
        assert len(results) == 3

    def test_create_deposit_success(
        self,
        injector_with_mocks,
        mock_account_repository,
        mock_transaction_repository,
        sample_account,
    ):
        """Test successfully creating a deposit"""
        # Setup: Add account to repository
        mock_account_repository.add(sample_account)
        initial_balance = int(sample_account.balance)  # type: ignore[arg-type]

        # Test: Create deposit
        service = injector_with_mocks.get(TransactionService)
        transaction = service.create_deposit(
            account_id=str(sample_account.id),
            amount=500,
            description="Test deposit",
        )

        # Verify transaction
        assert transaction is not None
        assert str(transaction.account_id) == str(sample_account.id)
        assert str(transaction.type) == "deposit"
        assert int(transaction.amount) == 500  # type: ignore[arg-type]
        assert str(transaction.description) == "Test deposit"

        # Verify balance was updated
        updated_account = mock_account_repository.get_by_id(str(sample_account.id))
        assert updated_account is not None
        assert int(updated_account.balance) == initial_balance + 500  # type: ignore[arg-type]

        # Verify transaction was recorded
        transactions = mock_transaction_repository.get_by_account_id(str(sample_account.id))
        assert len(transactions) == 1
        assert int(transactions[0].amount) == 500  # type: ignore[arg-type]

    def test_create_deposit_account_not_found(self, injector_with_mocks):
        """Test creating deposit for non-existent account raises error"""
        service = injector_with_mocks.get(TransactionService)

        with pytest.raises(ResourceNotFoundException) as exc_info:
            service.create_deposit(
                account_id="non-existent-id",
                amount=500,
                description="Test deposit",
            )

        # Verify exception details
        assert exc_info.value.resource_type == "Account"
        assert exc_info.value.resource_id == "non-existent-id"
        assert "not found" in str(exc_info.value)

    def test_create_deposit_updates_balance_correctly(
        self, injector_with_mocks, mock_account_repository, sample_account
    ):
        """Test that multiple deposits correctly update balance"""
        # Setup
        mock_account_repository.add(sample_account)
        initial_balance = int(sample_account.balance)  # type: ignore[arg-type]

        # Test: Create multiple deposits
        service = injector_with_mocks.get(TransactionService)
        service.create_deposit(str(sample_account.id), 100, "Deposit 1")
        service.create_deposit(str(sample_account.id), 200, "Deposit 2")
        service.create_deposit(str(sample_account.id), 300, "Deposit 3")

        # Verify: Final balance is correct
        updated_account = mock_account_repository.get_by_id(str(sample_account.id))
        assert updated_account is not None
        expected_balance = initial_balance + 100 + 200 + 300
        assert int(updated_account.balance) == expected_balance  # type: ignore[arg-type]

    def test_create_deposit_without_description(
        self, injector_with_mocks, mock_account_repository, sample_account
    ):
        """Test creating deposit without description"""
        # Setup
        mock_account_repository.add(sample_account)

        # Test: Create deposit without description
        service = injector_with_mocks.get(TransactionService)
        transaction = service.create_deposit(
            account_id=str(sample_account.id),
            amount=500,
        )

        # Verify
        assert transaction is not None
        assert transaction.description is None

    def test_create_deposit_with_negative_amount(
        self, injector_with_mocks, mock_account_repository, sample_account
    ):
        """Test creating deposit with negative amount raises error"""
        # Setup
        mock_account_repository.add(sample_account)

        # Test
        service = injector_with_mocks.get(TransactionService)
        with pytest.raises(InvalidAmountException) as exc_info:
            service.create_deposit(
                account_id=str(sample_account.id),
                amount=-100,
                description="Invalid deposit",
            )

        # Verify exception details
        assert exc_info.value.amount == -100
        assert "greater than zero" in exc_info.value.reason

    def test_create_deposit_with_zero_amount(
        self, injector_with_mocks, mock_account_repository, sample_account
    ):
        """Test creating deposit with zero amount raises error"""
        # Setup
        mock_account_repository.add(sample_account)

        # Test
        service = injector_with_mocks.get(TransactionService)
        with pytest.raises(InvalidAmountException) as exc_info:
            service.create_deposit(
                account_id=str(sample_account.id),
                amount=0,
                description="Zero deposit",
            )

        # Verify exception details
        assert exc_info.value.amount == 0
        assert "greater than zero" in exc_info.value.reason

    def test_service_uses_correct_repositories(
        self, mock_account_repository, mock_transaction_repository, sample_account
    ):
        """Test that TransactionService uses both injected repositories"""
        # Setup
        mock_account_repository.add(sample_account)

        # Create injector with specific repositories
        injector = Injector(
            [
                RepositoryModule(
                    MockProfileRepository(),
                    mock_account_repository,
                    mock_transaction_repository,
                ),
                ServiceModule(),
            ]
        )

        # Test
        service = injector.get(TransactionService)
        service.create_deposit(str(sample_account.id), 500, "Test")

        # Verify that both repositories were used
        assert mock_account_repository.get_by_id(str(sample_account.id)) is not None
        assert len(mock_transaction_repository.get_by_account_id(str(sample_account.id))) == 1


# ============================================================================
# WithdrawalRequestService Tests
# ============================================================================


class TestWithdrawalRequestService:
    """WithdrawalRequestService のテストスイート"""

    def test_create_withdrawal_request_success(
        self, mock_withdrawal_request_repository, mock_account_repository, sample_account
    ):
        """出金リクエスト作成の成功をテスト"""
        # Setup
        mock_account_repository.add(sample_account)

        injector = Injector(
            [
                RepositoryModule(
                    MockProfileRepository(),
                    mock_account_repository,
                    MockTransactionRepository(),
                    mock_withdrawal_request_repository,
                ),
                ServiceModule(),
            ]
        )

        service = injector.get(WithdrawalRequestService)

        # Test
        result = service.create_withdrawal_request(str(sample_account.id), 3000, "Snacks")

        # Assert
        assert result is not None
        assert int(result.amount) == 3000  # type: ignore[arg-type]
        assert str(result.status) == "pending"
        assert str(result.description) == "Snacks"

    def test_create_withdrawal_request_with_invalid_amount(
        self, mock_withdrawal_request_repository, mock_account_repository, sample_account
    ):
        """金額が0以下の場合にエラーをテスト"""
        mock_account_repository.add(sample_account)

        injector = Injector(
            [
                RepositoryModule(
                    MockProfileRepository(),
                    mock_account_repository,
                    MockTransactionRepository(),
                    mock_withdrawal_request_repository,
                ),
                ServiceModule(),
            ]
        )

        service = injector.get(WithdrawalRequestService)

        # 0の場合
        with pytest.raises(InvalidAmountException) as exc_info:
            service.create_withdrawal_request(str(sample_account.id), 0, "Test")
        assert exc_info.value.amount == 0

        # 負の場合
        with pytest.raises(InvalidAmountException) as exc_info:
            service.create_withdrawal_request(str(sample_account.id), -500, "Test")
        assert exc_info.value.amount == -500

    def test_create_withdrawal_request_account_not_found(
        self, mock_withdrawal_request_repository, mock_account_repository
    ):
        """存在しないアカウントの場合にエラーをテスト"""
        injector = Injector(
            [
                RepositoryModule(
                    MockProfileRepository(),
                    mock_account_repository,
                    MockTransactionRepository(),
                    mock_withdrawal_request_repository,
                ),
                ServiceModule(),
            ]
        )

        service = injector.get(WithdrawalRequestService)

        with pytest.raises(ResourceNotFoundException) as exc_info:
            service.create_withdrawal_request("non-existent-id", 1000, "Test")
        assert exc_info.value.resource_type == "Account"

    def test_create_withdrawal_request_insufficient_balance(
        self, mock_withdrawal_request_repository, mock_account_repository, sample_account
    ):
        """残高不足の場合にエラーをテスト"""
        # 残高10000のアカウント
        mock_account_repository.add(sample_account)

        injector = Injector(
            [
                RepositoryModule(
                    MockProfileRepository(),
                    mock_account_repository,
                    MockTransactionRepository(),
                    mock_withdrawal_request_repository,
                ),
                ServiceModule(),
            ]
        )

        service = injector.get(WithdrawalRequestService)

        # 残高を超える金額でリクエスト
        with pytest.raises(InvalidAmountException) as exc_info:
            service.create_withdrawal_request(str(sample_account.id), 15000, "Too much")
        assert "Insufficient balance" in exc_info.value.reason

    def test_get_pending_requests_for_parent(
        self, mock_withdrawal_request_repository, mock_account_repository, sample_account
    ):
        """親の子に対する保留中リクエスト取得をテスト"""
        mock_account_repository.add(sample_account)

        # 2件の出金リクエストを作成
        from datetime import UTC, datetime

        wr1 = mock_withdrawal_request_repository.create(
            account_id=str(sample_account.id),
            amount=1000,
            description="Request 1",
            created_at=datetime.now(UTC),
        )
        wr2 = mock_withdrawal_request_repository.create(
            account_id=str(sample_account.id),
            amount=1500,
            description="Request 2",
            created_at=datetime.now(UTC),
        )

        # 1件をapprovedに
        mock_withdrawal_request_repository.update_status(wr1, "approved", datetime.now(UTC))

        injector = Injector(
            [
                RepositoryModule(
                    MockProfileRepository(),
                    mock_account_repository,
                    MockTransactionRepository(),
                    mock_withdrawal_request_repository,
                ),
                ServiceModule(),
            ]
        )

        service = injector.get(WithdrawalRequestService)

        # Test
        results = service.get_pending_requests_for_parent("parent-id")

        # Assert - pendingのみ
        assert len(results) == 1
        assert str(results[0].id) == str(wr2.id)

    def test_approve_withdrawal_request_success(
        self,
        mock_withdrawal_request_repository,
        mock_account_repository,
        mock_transaction_repository,
        sample_account,
    ):
        """出金リクエスト承認の成功をテスト"""
        mock_account_repository.add(sample_account)

        # 出金リクエストを作成
        from datetime import UTC, datetime

        wr = mock_withdrawal_request_repository.create(
            account_id=str(sample_account.id),
            amount=3000,
            description="Approved request",
            created_at=datetime.now(UTC),
        )

        injector = Injector(
            [
                RepositoryModule(
                    MockProfileRepository(),
                    mock_account_repository,
                    mock_transaction_repository,
                    mock_withdrawal_request_repository,
                ),
                ServiceModule(),
            ]
        )

        service = injector.get(WithdrawalRequestService)
        transaction_service = injector.get(TransactionService)

        # Test
        result = service.approve_withdrawal_request(str(wr.id), transaction_service)

        # Assert
        assert str(result.status) == "approved"

        # 残高が減っていることを確認
        updated_account = mock_account_repository.get_by_id(str(sample_account.id))
        assert updated_account is not None
        assert int(updated_account.balance) == 10000 - 3000  # type: ignore[arg-type]

        # トランザクションが作成されたことを確認
        transactions = mock_transaction_repository.get_by_account_id(str(sample_account.id))
        assert len(transactions) == 1
        assert str(transactions[0].type) == "withdraw"
        assert int(transactions[0].amount) == 3000  # type: ignore[arg-type]

    def test_approve_withdrawal_request_not_found(
        self, mock_withdrawal_request_repository, mock_account_repository
    ):
        """存在しないリクエストの承認でエラーをテスト"""
        injector = Injector(
            [
                RepositoryModule(
                    MockProfileRepository(),
                    mock_account_repository,
                    MockTransactionRepository(),
                    mock_withdrawal_request_repository,
                ),
                ServiceModule(),
            ]
        )

        service = injector.get(WithdrawalRequestService)
        transaction_service = injector.get(TransactionService)

        with pytest.raises(ResourceNotFoundException) as exc_info:
            service.approve_withdrawal_request("non-existent-id", transaction_service)
        assert exc_info.value.resource_type == "WithdrawalRequest"

    def test_approve_withdrawal_request_already_processed(
        self,
        mock_withdrawal_request_repository,
        mock_account_repository,
        mock_transaction_repository,
        sample_account,
    ):
        """既に処理済みのリクエスト承認でエラーをテスト"""
        mock_account_repository.add(sample_account)

        from datetime import UTC, datetime

        wr = mock_withdrawal_request_repository.create(
            account_id=str(sample_account.id),
            amount=2000,
            description="Already approved",
            created_at=datetime.now(UTC),
        )

        # 先に承認済みに
        mock_withdrawal_request_repository.update_status(wr, "approved", datetime.now(UTC))

        injector = Injector(
            [
                RepositoryModule(
                    MockProfileRepository(),
                    mock_account_repository,
                    mock_transaction_repository,
                    mock_withdrawal_request_repository,
                ),
                ServiceModule(),
            ]
        )

        service = injector.get(WithdrawalRequestService)
        transaction_service = injector.get(TransactionService)

        with pytest.raises(InvalidAmountException) as exc_info:
            service.approve_withdrawal_request(str(wr.id), transaction_service)
        assert "already approved" in exc_info.value.reason

    def test_reject_withdrawal_request_success(
        self,
        mock_withdrawal_request_repository,
        mock_account_repository,
        mock_transaction_repository,
        sample_account,
    ):
        """出金リクエスト却下の成功をテスト"""
        mock_account_repository.add(sample_account)

        from datetime import UTC, datetime

        wr = mock_withdrawal_request_repository.create(
            account_id=str(sample_account.id),
            amount=2000,
            description="To be rejected",
            created_at=datetime.now(UTC),
        )

        injector = Injector(
            [
                RepositoryModule(
                    MockProfileRepository(),
                    mock_account_repository,
                    mock_transaction_repository,
                    mock_withdrawal_request_repository,
                ),
                ServiceModule(),
            ]
        )

        service = injector.get(WithdrawalRequestService)

        # Test
        result = service.reject_withdrawal_request(str(wr.id))

        # Assert
        assert str(result.status) == "rejected"

        # 残高は変わらない
        updated_account = mock_account_repository.get_by_id(str(sample_account.id))
        assert updated_account is not None
        assert int(updated_account.balance) == 10000  # type: ignore[arg-type]

        # トランザクションは作成されない
        transactions = mock_transaction_repository.get_by_account_id(str(sample_account.id))
        assert len(transactions) == 0

    def test_reject_withdrawal_request_not_found(
        self, mock_withdrawal_request_repository, mock_account_repository
    ):
        """存在しないリクエストの却下でエラーをテスト"""
        injector = Injector(
            [
                RepositoryModule(
                    MockProfileRepository(),
                    mock_account_repository,
                    MockTransactionRepository(),
                    mock_withdrawal_request_repository,
                ),
                ServiceModule(),
            ]
        )

        service = injector.get(WithdrawalRequestService)

        with pytest.raises(ResourceNotFoundException) as exc_info:
            service.reject_withdrawal_request("non-existent-id")
        assert exc_info.value.resource_type == "WithdrawalRequest"

    def test_reject_withdrawal_request_already_processed(
        self, mock_withdrawal_request_repository, mock_account_repository, sample_account
    ):
        """既に処理済みのリクエスト却下でエラーをテスト"""
        mock_account_repository.add(sample_account)

        from datetime import UTC, datetime

        wr = mock_withdrawal_request_repository.create(
            account_id=str(sample_account.id),
            amount=1000,
            description="Already rejected",
            created_at=datetime.now(UTC),
        )

        # 先に却下済みに
        mock_withdrawal_request_repository.update_status(wr, "rejected", datetime.now(UTC))

        injector = Injector(
            [
                RepositoryModule(
                    MockProfileRepository(),
                    mock_account_repository,
                    MockTransactionRepository(),
                    mock_withdrawal_request_repository,
                ),
                ServiceModule(),
            ]
        )

        service = injector.get(WithdrawalRequestService)

        with pytest.raises(InvalidAmountException) as exc_info:
            service.reject_withdrawal_request(str(wr.id))
        assert "already rejected" in exc_info.value.reason


class TestRecurringDepositService:
    """RecurringDepositService のビジネスロジックをテスト"""

    def test_get_recurring_deposit_by_parent(
        self,
        mock_profile_repository,
        mock_account_repository,
        mock_recurring_deposit_repository,
        sample_profile,
        sample_child,
        sample_account,
    ):
        """親が子供の定期入金設定を取得できることをテスト"""
        # プロフィールとアカウントを準備
        mock_profile_repository.add(sample_profile)
        sample_child.parent_id = sample_profile.id
        mock_profile_repository.add(sample_child)
        sample_account.user_id = sample_child.id
        mock_account_repository.add(sample_account)

        # 定期入金設定を作成
        rd = mock_recurring_deposit_repository.create(
            account_id=str(sample_account.id),
            amount=5000,
            day_of_month=15,
            created_at=datetime.now(UTC),
        )

        injector = Injector(
            [
                RepositoryModule(
                    mock_profile_repository,
                    mock_account_repository,
                    MockTransactionRepository(),
                    MockWithdrawalRequestRepository(),
                    mock_recurring_deposit_repository,
                ),
                ServiceModule(),
            ]
        )

        service = injector.get(RecurringDepositService)

        # 親が子供のアカウントの定期入金設定を取得
        result = service.get_recurring_deposit(str(sample_account.id), str(sample_profile.id))

        assert result is not None
        assert result.id == rd.id
        assert result.amount == 5000

    def test_get_recurring_deposit_account_not_found(
        self, mock_profile_repository, mock_account_repository, mock_recurring_deposit_repository
    ):
        """存在しないアカウントの定期入金設定を取得しようとするとエラーになることをテスト"""
        injector = Injector(
            [
                RepositoryModule(
                    mock_profile_repository,
                    mock_account_repository,
                    MockTransactionRepository(),
                    MockWithdrawalRequestRepository(),
                    mock_recurring_deposit_repository,
                ),
                ServiceModule(),
            ]
        )

        service = injector.get(RecurringDepositService)

        with pytest.raises(ResourceNotFoundException) as exc_info:
            service.get_recurring_deposit(str(uuid.uuid4()), str(uuid.uuid4()))
        assert "Account" in str(exc_info.value)

    def test_create_or_update_recurring_deposit_create_new(
        self,
        mock_profile_repository,
        mock_account_repository,
        mock_recurring_deposit_repository,
        sample_profile,
        sample_child,
        sample_account,
    ):
        """新しい定期入金設定を作成できることをテスト"""
        # プロフィールとアカウントを準備
        mock_profile_repository.add(sample_profile)
        sample_child.parent_id = sample_profile.id
        mock_profile_repository.add(sample_child)
        sample_account.user_id = sample_child.id
        mock_account_repository.add(sample_account)

        injector = Injector(
            [
                RepositoryModule(
                    mock_profile_repository,
                    mock_account_repository,
                    MockTransactionRepository(),
                    MockWithdrawalRequestRepository(),
                    mock_recurring_deposit_repository,
                ),
                ServiceModule(),
            ]
        )

        service = injector.get(RecurringDepositService)

        # 親が子供のアカウントに定期入金設定を作成
        result = service.create_or_update_recurring_deposit(
            account_id=str(sample_account.id),
            current_user_id=str(sample_profile.id),
            amount=3000,
            day_of_month=1,
            is_active=True,
        )

        assert result is not None
        assert result.amount == 3000
        assert result.day_of_month == 1
        assert result.is_active is True

    def test_create_or_update_recurring_deposit_update_existing(
        self,
        mock_profile_repository,
        mock_account_repository,
        mock_recurring_deposit_repository,
        sample_profile,
        sample_child,
        sample_account,
    ):
        """既存の定期入金設定を更新できることをテスト"""
        # プロフィールとアカウントを準備
        mock_profile_repository.add(sample_profile)
        sample_child.parent_id = sample_profile.id
        mock_profile_repository.add(sample_child)
        sample_account.user_id = sample_child.id
        mock_account_repository.add(sample_account)

        # 既存の定期入金設定を作成
        existing = mock_recurring_deposit_repository.create(
            account_id=str(sample_account.id),
            amount=5000,
            day_of_month=15,
            created_at=datetime.now(UTC),
        )

        injector = Injector(
            [
                RepositoryModule(
                    mock_profile_repository,
                    mock_account_repository,
                    MockTransactionRepository(),
                    MockWithdrawalRequestRepository(),
                    mock_recurring_deposit_repository,
                ),
                ServiceModule(),
            ]
        )

        service = injector.get(RecurringDepositService)

        # 親が子供のアカウントの定期入金設定を更新
        result = service.create_or_update_recurring_deposit(
            account_id=str(sample_account.id),
            current_user_id=str(sample_profile.id),
            amount=10000,
            day_of_month=25,
            is_active=False,
        )

        assert result is not None
        assert result.id == existing.id
        assert result.amount == 10000
        assert result.day_of_month == 25
        assert result.is_active is False

    def test_create_or_update_recurring_deposit_with_invalid_amount(
        self,
        mock_profile_repository,
        mock_account_repository,
        mock_recurring_deposit_repository,
        sample_profile,
        sample_child,
        sample_account,
    ):
        """不正な金額で定期入金設定を作成しようとするとエラーになることをテスト"""
        # プロフィールとアカウントを準備
        mock_profile_repository.add(sample_profile)
        sample_child.parent_id = sample_profile.id
        mock_profile_repository.add(sample_child)
        sample_account.user_id = sample_child.id
        mock_account_repository.add(sample_account)

        injector = Injector(
            [
                RepositoryModule(
                    mock_profile_repository,
                    mock_account_repository,
                    MockTransactionRepository(),
                    MockWithdrawalRequestRepository(),
                    mock_recurring_deposit_repository,
                ),
                ServiceModule(),
            ]
        )

        service = injector.get(RecurringDepositService)

        # 負の金額
        with pytest.raises(InvalidAmountException) as exc_info:
            service.create_or_update_recurring_deposit(
                account_id=str(sample_account.id),
                current_user_id=str(sample_profile.id),
                amount=-100,
                day_of_month=1,
            )
        assert "positive" in exc_info.value.reason

        # ゼロの金額
        with pytest.raises(InvalidAmountException) as exc_info:
            service.create_or_update_recurring_deposit(
                account_id=str(sample_account.id),
                current_user_id=str(sample_profile.id),
                amount=0,
                day_of_month=1,
            )
        assert "positive" in exc_info.value.reason

    def test_create_or_update_recurring_deposit_with_invalid_day(
        self,
        mock_profile_repository,
        mock_account_repository,
        mock_recurring_deposit_repository,
        sample_profile,
        sample_child,
        sample_account,
    ):
        """不正な日付で定期入金設定を作成しようとするとエラーになることをテスト"""
        # プロフィールとアカウントを準備
        mock_profile_repository.add(sample_profile)
        sample_child.parent_id = sample_profile.id
        mock_profile_repository.add(sample_child)
        sample_account.user_id = sample_child.id
        mock_account_repository.add(sample_account)

        injector = Injector(
            [
                RepositoryModule(
                    mock_profile_repository,
                    mock_account_repository,
                    MockTransactionRepository(),
                    MockWithdrawalRequestRepository(),
                    mock_recurring_deposit_repository,
                ),
                ServiceModule(),
            ]
        )

        service = injector.get(RecurringDepositService)

        # 範囲外の日付（0）
        with pytest.raises(InvalidAmountException) as exc_info:
            service.create_or_update_recurring_deposit(
                account_id=str(sample_account.id),
                current_user_id=str(sample_profile.id),
                amount=5000,
                day_of_month=0,
            )
        assert "between 1 and 31" in exc_info.value.reason

        # 範囲外の日付（32）
        with pytest.raises(InvalidAmountException) as exc_info:
            service.create_or_update_recurring_deposit(
                account_id=str(sample_account.id),
                current_user_id=str(sample_profile.id),
                amount=5000,
                day_of_month=32,
            )
        assert "between 1 and 31" in exc_info.value.reason

    def test_delete_recurring_deposit_success(
        self,
        mock_profile_repository,
        mock_account_repository,
        mock_recurring_deposit_repository,
        sample_profile,
        sample_child,
        sample_account,
    ):
        """定期入金設定を削除できることをテスト"""
        # プロフィールとアカウントを準備
        mock_profile_repository.add(sample_profile)
        sample_child.parent_id = sample_profile.id
        mock_profile_repository.add(sample_child)
        sample_account.user_id = sample_child.id
        mock_account_repository.add(sample_account)

        # 定期入金設定を作成
        mock_recurring_deposit_repository.create(
            account_id=str(sample_account.id),
            amount=5000,
            day_of_month=15,
            created_at=datetime.now(UTC),
        )

        injector = Injector(
            [
                RepositoryModule(
                    mock_profile_repository,
                    mock_account_repository,
                    MockTransactionRepository(),
                    MockWithdrawalRequestRepository(),
                    mock_recurring_deposit_repository,
                ),
                ServiceModule(),
            ]
        )

        service = injector.get(RecurringDepositService)

        # 親が子供のアカウントの定期入金設定を削除
        result = service.delete_recurring_deposit(
            account_id=str(sample_account.id), current_user_id=str(sample_profile.id)
        )

        assert result is True

        # 削除後は取得できない
        deleted = service.get_recurring_deposit(str(sample_account.id), str(sample_profile.id))
        assert deleted is None

    def test_delete_recurring_deposit_not_found(
        self,
        mock_profile_repository,
        mock_account_repository,
        mock_recurring_deposit_repository,
        sample_profile,
        sample_child,
        sample_account,
    ):
        """存在しない定期入金設定を削除しようとするとエラーになることをテスト"""
        # プロフィールとアカウントを準備
        mock_profile_repository.add(sample_profile)
        sample_child.parent_id = sample_profile.id
        mock_profile_repository.add(sample_child)
        sample_account.user_id = sample_child.id
        mock_account_repository.add(sample_account)

        injector = Injector(
            [
                RepositoryModule(
                    mock_profile_repository,
                    mock_account_repository,
                    MockTransactionRepository(),
                    MockWithdrawalRequestRepository(),
                    mock_recurring_deposit_repository,
                ),
                ServiceModule(),
            ]
        )

        service = injector.get(RecurringDepositService)

        with pytest.raises(ResourceNotFoundException) as exc_info:
            service.delete_recurring_deposit(
                account_id=str(sample_account.id), current_user_id=str(sample_profile.id)
            )
        assert "RecurringDeposit" in str(exc_info.value)

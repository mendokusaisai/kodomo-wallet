"""
Unit tests for Service layer business logic.

Tests ProfileService, AccountService, and TransactionService
using mock repositories via dependency injection.
"""

import uuid
from datetime import UTC, datetime

import pytest
from injector import Binder, Injector, Module

from app.models.models import Account, Profile
from app.repositories.interfaces import (
    AccountRepository,
    ProfileRepository,
    TransactionRepository,
)
from app.repositories.mock_repositories import (
    MockAccountRepository,
    MockProfileRepository,
    MockTransactionRepository,
)
from app.services.business_services import (
    AccountService,
    ProfileService,
    TransactionService,
)

# ============================================================================
# Test Module for Dependency Injection
# ============================================================================


class TestRepositoryModule(Module):
    """Module that provides mock repositories for testing"""

    def __init__(
        self,
        profile_repo: MockProfileRepository,
        account_repo: MockAccountRepository,
        transaction_repo: MockTransactionRepository,
    ):
        self.profile_repo = profile_repo
        self.account_repo = account_repo
        self.transaction_repo = transaction_repo

    def configure(self, binder: Binder) -> None:
        """Bind mock repositories"""
        binder.bind(ProfileRepository, to=self.profile_repo)
        binder.bind(AccountRepository, to=self.account_repo)
        binder.bind(TransactionRepository, to=self.transaction_repo)


class TestServiceModule(Module):
    """Module that provides service instances"""

    def configure(self, binder: Binder) -> None:
        """Bind services"""
        binder.bind(ProfileService, to=ProfileService)
        binder.bind(AccountService, to=AccountService)
        binder.bind(TransactionService, to=TransactionService)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_profile_repository():
    """Create a mock profile repository"""
    return MockProfileRepository()


@pytest.fixture
def mock_account_repository():
    """Create a mock account repository"""
    return MockAccountRepository()


@pytest.fixture
def mock_transaction_repository():
    """Create a mock transaction repository"""
    return MockTransactionRepository()


@pytest.fixture
def injector_with_mocks(mock_profile_repo, mock_account_repository, mock_transaction_repo):
    """Create an injector with mock repositories"""
    return Injector(
        [
            TestRepositoryModule(
                mock_profile_repo,
                mock_account_repository,
                mock_transaction_repo,
            ),
            TestServiceModule(),
        ]
    )


@pytest.fixture
def sample_profile():
    """Create a sample profile"""
    return Profile(
        id=uuid.uuid4(),
        name="Test User",
        role="parent",
        created_at=str(datetime.now(UTC)),
        updated_at=str(datetime.now(UTC)),
    )


@pytest.fixture
def sample_account(sample_profile):
    """Create a sample account"""
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
    """Test suite for ProfileService"""

    def test_get_profile_success(
        self, injector_with_mocks, mock_profile_repository, sample_profile
    ):
        """Test successfully retrieving a profile"""
        # Setup: Add profile to mock repository
        mock_profile_repository.add(sample_profile)

        # Test: Get service and retrieve profile
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
        self, mock_profile_repo, mock_account_repository, mock_transaction_repo, sample_profile
    ):
        """Test that ProfileService uses the injected repository"""
        # Setup: Create service with specific repository
        mock_profile_repo.add(sample_profile)

        injector = Injector(
            [
                TestRepositoryModule(
                    mock_profile_repo,
                    mock_account_repository,
                    mock_transaction_repo,
                ),
                TestServiceModule(),
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
        self, injector_with_mocks, mock_account_repository, mock_transaction_repo, sample_account
    ):
        """Test successfully retrieving account transactions"""
        # Setup: Add account and transactions
        mock_account_repository.add(sample_account)
        mock_transaction_repo.create(
            account_id=str(sample_account.id),
            transaction_type="deposit",
            amount=1000,
            description="Test 1",
            created_at=str(datetime.now(UTC)),
        )
        mock_transaction_repo.create(
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
        self, injector_with_mocks, mock_account_repository, mock_transaction_repo, sample_account
    ):
        """Test retrieving transactions with limit"""
        # Setup: Add account and multiple transactions
        mock_account_repository.add(sample_account)
        for i in range(5):
            mock_transaction_repo.create(
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
        self, injector_with_mocks, mock_account_repository, mock_transaction_repo, sample_account
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
        transactions = mock_transaction_repo.get_by_account_id(str(sample_account.id))
        assert len(transactions) == 1
        assert int(transactions[0].amount) == 500  # type: ignore[arg-type]

    def test_create_deposit_account_not_found(self, injector_with_mocks):
        """Test creating deposit for non-existent account raises error"""
        service = injector_with_mocks.get(TransactionService)

        with pytest.raises(ValueError, match="Account not found"):
            service.create_deposit(
                account_id="non-existent-id",
                amount=500,
                description="Test deposit",
            )

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

    def test_service_uses_correct_repositories(
        self, mock_account_repository, mock_transaction_repo, sample_account
    ):
        """Test that TransactionService uses both injected repositories"""
        # Setup
        mock_account_repository.add(sample_account)

        # Create injector with specific repositories
        injector = Injector(
            [
                TestRepositoryModule(
                    MockProfileRepository(),
                    mock_account_repository,
                    mock_transaction_repo,
                ),
                TestServiceModule(),
            ]
        )

        # Test
        service = injector.get(TransactionService)
        service.create_deposit(str(sample_account.id), 500, "Test")

        # Verify that both repositories were used
        assert mock_account_repository.get_by_id(str(sample_account.id)) is not None
        assert len(mock_transaction_repo.get_by_account_id(str(sample_account.id))) == 1

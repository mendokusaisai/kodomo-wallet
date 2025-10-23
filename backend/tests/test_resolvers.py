"""
Unit tests for GraphQL resolvers.

Tests resolver functions with mocked service dependencies.
"""

import uuid
from datetime import UTC, datetime
from unittest.mock import Mock

import pytest
from sqlalchemy.orm import Session

from app.api.graphql import resolvers
from app.models.models import Account, Profile, Transaction


@pytest.fixture
def mock_profile_service():
    """Create a mock ProfileService"""
    return Mock()


@pytest.fixture
def mock_account_service():
    """Create a mock AccountService"""
    return Mock()


@pytest.fixture
def mock_transaction_service():
    """Create a mock TransactionService"""
    return Mock()


@pytest.fixture
def mock_db_session():
    """Create a mock database session"""
    return Mock(spec=Session)


@pytest.fixture
def sample_profile():
    """Create a sample profile for testing"""
    return Profile(
        id=uuid.uuid4(),
        name="Test User",
        role="parent",
        created_at=str(datetime.now(UTC)),
        updated_at=str(datetime.now(UTC)),
    )


@pytest.fixture
def sample_account():
    """Create a sample account for testing"""
    return Account(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        balance=10000,
        currency="JPY",
        goal_name="Test Goal",
        goal_amount=50000,
        created_at=str(datetime.now(UTC)),
        updated_at=str(datetime.now(UTC)),
    )


@pytest.fixture
def sample_transaction():
    """Create a sample transaction for testing"""
    return Transaction(
        id=uuid.uuid4(),
        account_id=uuid.uuid4(),
        type="deposit",
        amount=1000,
        description="Test deposit",
        created_at=str(datetime.now(UTC)),
    )


class TestGetProfileById:
    """Tests for get_profile_by_id resolver"""

    def test_get_profile_by_id_success(self, mock_profile_service, sample_profile):
        """Test successful profile retrieval"""
        # Arrange
        user_id = str(sample_profile.id)
        mock_profile_service.get_profile.return_value = sample_profile

        # Act
        result = resolvers.get_profile_by_id(user_id, mock_profile_service)

        # Assert
        assert result == sample_profile
        mock_profile_service.get_profile.assert_called_once_with(user_id)

    def test_get_profile_by_id_not_found(self, mock_profile_service):
        """Test profile not found returns None"""
        # Arrange
        user_id = str(uuid.uuid4())
        mock_profile_service.get_profile.return_value = None

        # Act
        result = resolvers.get_profile_by_id(user_id, mock_profile_service)

        # Assert
        assert result is None
        mock_profile_service.get_profile.assert_called_once_with(user_id)

    def test_get_profile_by_id_with_invalid_id(self, mock_profile_service):
        """Test profile retrieval with invalid ID"""
        # Arrange
        invalid_id = "invalid-uuid"
        mock_profile_service.get_profile.return_value = None

        # Act
        result = resolvers.get_profile_by_id(invalid_id, mock_profile_service)

        # Assert
        assert result is None
        mock_profile_service.get_profile.assert_called_once_with(invalid_id)


class TestGetAccountsByUserId:
    """Tests for get_accounts_by_user_id resolver"""

    def test_get_accounts_by_user_id_success(self, mock_account_service, sample_account):
        """Test successful accounts retrieval"""
        # Arrange
        user_id = str(sample_account.user_id)
        accounts = [sample_account]
        mock_account_service.get_user_accounts.return_value = accounts

        # Act
        result = resolvers.get_accounts_by_user_id(user_id, mock_account_service)

        # Assert
        assert result == accounts
        assert len(result) == 1
        assert result[0] == sample_account
        mock_account_service.get_user_accounts.assert_called_once_with(user_id)

    def test_get_accounts_by_user_id_empty(self, mock_account_service):
        """Test accounts retrieval with no results"""
        # Arrange
        user_id = str(uuid.uuid4())
        mock_account_service.get_user_accounts.return_value = []

        # Act
        result = resolvers.get_accounts_by_user_id(user_id, mock_account_service)

        # Assert
        assert result == []
        mock_account_service.get_user_accounts.assert_called_once_with(user_id)

    def test_get_accounts_by_user_id_multiple(self, mock_account_service, sample_account):
        """Test accounts retrieval with multiple results"""
        # Arrange
        user_id = str(sample_account.user_id)
        account2 = Account(
            id=uuid.uuid4(),
            user_id=sample_account.user_id,
            balance=20000,
            currency="JPY",
            goal_name="Another Goal",
            goal_amount=100000,
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        accounts = [sample_account, account2]
        mock_account_service.get_user_accounts.return_value = accounts

        # Act
        result = resolvers.get_accounts_by_user_id(user_id, mock_account_service)

        # Assert
        assert result == accounts
        assert len(result) == 2
        mock_account_service.get_user_accounts.assert_called_once_with(user_id)


class TestGetTransactionsByAccountId:
    """Tests for get_transactions_by_account_id resolver"""

    def test_get_transactions_by_account_id_success(
        self, mock_transaction_service, sample_transaction
    ):
        """Test successful transactions retrieval"""
        # Arrange
        account_id = str(sample_transaction.account_id)
        transactions = [sample_transaction]
        mock_transaction_service.get_account_transactions.return_value = transactions

        # Act
        result = resolvers.get_transactions_by_account_id(account_id, mock_transaction_service)

        # Assert
        assert result == transactions
        assert len(result) == 1
        assert result[0] == sample_transaction
        mock_transaction_service.get_account_transactions.assert_called_once_with(account_id, 50)

    def test_get_transactions_by_account_id_with_custom_limit(
        self, mock_transaction_service, sample_transaction
    ):
        """Test transactions retrieval with custom limit"""
        # Arrange
        account_id = str(sample_transaction.account_id)
        transactions = [sample_transaction]
        mock_transaction_service.get_account_transactions.return_value = transactions
        custom_limit = 10

        # Act
        result = resolvers.get_transactions_by_account_id(
            account_id, mock_transaction_service, limit=custom_limit
        )

        # Assert
        assert result == transactions
        mock_transaction_service.get_account_transactions.assert_called_once_with(
            account_id, custom_limit
        )

    def test_get_transactions_by_account_id_empty(self, mock_transaction_service):
        """Test transactions retrieval with no results"""
        # Arrange
        account_id = str(uuid.uuid4())
        mock_transaction_service.get_account_transactions.return_value = []

        # Act
        result = resolvers.get_transactions_by_account_id(account_id, mock_transaction_service)

        # Assert
        assert result == []
        mock_transaction_service.get_account_transactions.assert_called_once_with(account_id, 50)

    def test_get_transactions_by_account_id_multiple(
        self, mock_transaction_service, sample_transaction
    ):
        """Test transactions retrieval with multiple results"""
        # Arrange
        account_id = str(sample_transaction.account_id)
        transaction2 = Transaction(
            id=uuid.uuid4(),
            account_id=sample_transaction.account_id,
            type="withdrawal",
            amount=500,
            description="Test withdrawal",
            created_at=str(datetime.now(UTC)),
        )
        transactions = [sample_transaction, transaction2]
        mock_transaction_service.get_account_transactions.return_value = transactions

        # Act
        result = resolvers.get_transactions_by_account_id(account_id, mock_transaction_service)

        # Assert
        assert result == transactions
        assert len(result) == 2
        mock_transaction_service.get_account_transactions.assert_called_once_with(account_id, 50)


class TestCreateDeposit:
    """Tests for create_deposit resolver"""

    def test_create_deposit_success(
        self, mock_transaction_service, mock_db_session, sample_transaction
    ):
        """Test successful deposit creation"""
        # Arrange
        account_id = str(sample_transaction.account_id)
        amount = 1000
        description = "Test deposit"
        mock_transaction_service.create_deposit.return_value = sample_transaction

        # Act
        result = resolvers.create_deposit(
            account_id,
            amount,
            mock_db_session,
            mock_transaction_service,
            description=description,
        )

        # Assert
        assert result == sample_transaction
        mock_transaction_service.create_deposit.assert_called_once_with(
            account_id, amount, description
        )
        mock_db_session.commit.assert_called_once()

    def test_create_deposit_without_description(
        self, mock_transaction_service, mock_db_session, sample_transaction
    ):
        """Test deposit creation without description"""
        # Arrange
        account_id = str(sample_transaction.account_id)
        amount = 1000
        mock_transaction_service.create_deposit.return_value = sample_transaction

        # Act
        result = resolvers.create_deposit(
            account_id, amount, mock_db_session, mock_transaction_service
        )

        # Assert
        assert result == sample_transaction
        mock_transaction_service.create_deposit.assert_called_once_with(account_id, amount, None)
        mock_db_session.commit.assert_called_once()

    def test_create_deposit_commits_transaction(
        self, mock_transaction_service, mock_db_session, sample_transaction
    ):
        """Test that deposit creation commits the database transaction"""
        # Arrange
        account_id = str(sample_transaction.account_id)
        amount = 1000
        mock_transaction_service.create_deposit.return_value = sample_transaction

        # Act
        resolvers.create_deposit(account_id, amount, mock_db_session, mock_transaction_service)

        # Assert
        mock_db_session.commit.assert_called_once()

    def test_create_deposit_with_service_exception(self, mock_transaction_service, mock_db_session):
        """Test deposit creation when service raises an exception"""
        # Arrange
        account_id = str(uuid.uuid4())
        amount = 1000
        mock_transaction_service.create_deposit.side_effect = ValueError("Account not found")

        # Act & Assert
        with pytest.raises(ValueError, match="Account not found"):
            resolvers.create_deposit(account_id, amount, mock_db_session, mock_transaction_service)

        # Verify commit was not called due to exception
        mock_db_session.commit.assert_not_called()

    def test_create_deposit_with_large_amount(
        self, mock_transaction_service, mock_db_session, sample_transaction
    ):
        """Test deposit creation with large amount"""
        # Arrange
        account_id = str(sample_transaction.account_id)
        amount = 1000000
        large_transaction = Transaction(
            id=sample_transaction.id,
            account_id=sample_transaction.account_id,
            type="deposit",
            amount=amount,
            description="Large deposit",
            created_at=str(datetime.now(UTC)),
        )
        mock_transaction_service.create_deposit.return_value = large_transaction

        # Act
        result = resolvers.create_deposit(
            account_id,
            amount,
            mock_db_session,
            mock_transaction_service,
            description="Large deposit",
        )

        # Assert
        assert result == large_transaction
        assert result.amount == amount
        mock_transaction_service.create_deposit.assert_called_once_with(
            account_id, amount, "Large deposit"
        )
        mock_db_session.commit.assert_called_once()

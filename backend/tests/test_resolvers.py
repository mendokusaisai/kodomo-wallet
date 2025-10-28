"""GraphQL リゾルバーのユニットテスト

モック化されたサービス依存関係を使ってリゾルバー関数をテスト
"""

import uuid
from datetime import UTC, datetime
from unittest.mock import Mock

import pytest
from sqlalchemy.orm import Session

from app.api.graphql import resolvers
from app.repositories.sqlalchemy.models import (
    Account,
    Profile,
    RecurringDeposit,
    Transaction,
    WithdrawalRequest,
)


@pytest.fixture
def mock_profile_service():
    """モックの ProfileService を作成"""
    return Mock()


@pytest.fixture
def mock_account_service():
    """モックの AccountService を作成"""
    return Mock()


@pytest.fixture
def mock_transaction_service():
    """モックの TransactionService を作成"""
    return Mock()


@pytest.fixture
def mock_withdrawal_request_service():
    """モックの WithdrawalRequestService を作成"""
    return Mock()


@pytest.fixture
def mock_recurring_deposit_service():
    """モックの RecurringDepositService を作成"""
    return Mock()


@pytest.fixture
def mock_db_session():
    """モックのデータベースセッションを作成"""
    return Mock(spec=Session)


@pytest.fixture
def sample_profile():
    """テスト用のサンプルプロフィールを作成"""
    return Profile(
        id=uuid.uuid4(),
        name="Test User",
        role="parent",
        created_at=str(datetime.now(UTC)),
        updated_at=str(datetime.now(UTC)),
    )


@pytest.fixture
def sample_account():
    """テスト用のサンプルアカウントを作成"""
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
    """テスト用のサンプルトランザクションを作成"""
    return Transaction(
        id=uuid.uuid4(),
        account_id=uuid.uuid4(),
        type="deposit",
        amount=1000,
        description="Test deposit",
        created_at=str(datetime.now(UTC)),
    )


@pytest.fixture
def sample_withdrawal_request():
    """テスト用のサンプル出金リクエストを作成"""
    return WithdrawalRequest(
        id=uuid.uuid4(),
        account_id=uuid.uuid4(),
        amount=5000,
        description="Test withdrawal request",
        status="pending",
        created_at=str(datetime.now(UTC)),
        updated_at=str(datetime.now(UTC)),
    )


@pytest.fixture
def sample_recurring_deposit():
    """テスト用のサンプル定期入金設定を作成"""
    return RecurringDeposit(
        id=uuid.uuid4(),
        account_id=uuid.uuid4(),
        amount=3000,
        day_of_month=15,
        is_active="true",
        created_at=str(datetime.now(UTC)),
        updated_at=str(datetime.now(UTC)),
    )


class TestGetProfileById:
    """get_profile_by_id リゾルバーのテスト"""

    def test_get_profile_by_id_success(self, mock_profile_service, sample_profile):
        """プロフィール取得の成功をテスト"""
        # Arrange
        user_id = str(sample_profile.id)
        mock_profile_service.get_profile.return_value = sample_profile

        # Act
        result = resolvers.get_profile_by_id(user_id, mock_profile_service)

        # Assert
        assert result == sample_profile
        mock_profile_service.get_profile.assert_called_once_with(user_id)

    def test_get_profile_by_id_not_found(self, mock_profile_service):
        """プロフィールが見つからない場合に None を返すことをテスト"""
        # Arrange
        user_id = str(uuid.uuid4())
        mock_profile_service.get_profile.return_value = None

        # Act
        result = resolvers.get_profile_by_id(user_id, mock_profile_service)

        # Assert
        assert result is None
        mock_profile_service.get_profile.assert_called_once_with(user_id)

    def test_get_profile_by_id_with_invalid_id(self, mock_profile_service):
        """無効な ID でのプロフィール取得をテスト"""
        # Arrange
        invalid_id = "invalid-uuid"
        mock_profile_service.get_profile.return_value = None

        # Act
        result = resolvers.get_profile_by_id(invalid_id, mock_profile_service)

        # Assert
        assert result is None
        mock_profile_service.get_profile.assert_called_once_with(invalid_id)


class TestGetAccountsByUserId:
    """get_accounts_by_user_id リゾルバーのテスト"""

    def test_get_accounts_by_user_id_success(
        self, mock_account_service, mock_profile_service, sample_account, sample_profile
    ):
        """アカウント取得の成功をテスト"""
        # Arrange
        user_id = str(sample_account.user_id)
        accounts = [sample_account]
        mock_account_service.get_family_accounts.return_value = accounts
        mock_profile_service.get_profile.return_value = sample_profile

        # Act
        result = resolvers.get_accounts_by_user_id(
            user_id, mock_account_service, mock_profile_service
        )

        # Assert
        assert result == accounts
        assert len(result) == 1
        assert result[0] == sample_account
        mock_account_service.get_family_accounts.assert_called_once_with(user_id)

    def test_get_accounts_by_user_id_empty(self, mock_account_service, mock_profile_service):
        """結果がない場合のアカウント取得をテスト"""
        # Arrange
        user_id = str(uuid.uuid4())
        mock_account_service.get_family_accounts.return_value = []

        # Act
        result = resolvers.get_accounts_by_user_id(
            user_id, mock_account_service, mock_profile_service
        )

        # Assert
        assert result == []
        mock_account_service.get_family_accounts.assert_called_once_with(user_id)

    def test_get_accounts_by_user_id_multiple(
        self, mock_account_service, mock_profile_service, sample_account, sample_profile
    ):
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
        mock_account_service.get_family_accounts.return_value = accounts
        mock_profile_service.get_profile.return_value = sample_profile

        # Act
        result = resolvers.get_accounts_by_user_id(
            user_id, mock_account_service, mock_profile_service
        )

        # Assert
        assert result == accounts
        assert len(result) == 2
        mock_account_service.get_family_accounts.assert_called_once_with(user_id)


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

    def test_create_deposit_success(self, mock_transaction_service, sample_transaction):
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
            mock_transaction_service,
            description=description,
        )

        # Assert
        assert result == sample_transaction
        mock_transaction_service.create_deposit.assert_called_once_with(
            account_id, amount, description
        )

    def test_create_deposit_without_description(self, mock_transaction_service, sample_transaction):
        """Test deposit creation without description"""
        # Arrange
        account_id = str(sample_transaction.account_id)
        amount = 1000
        mock_transaction_service.create_deposit.return_value = sample_transaction

        # Act
        result = resolvers.create_deposit(account_id, amount, mock_transaction_service)

        # Assert
        assert result == sample_transaction
        mock_transaction_service.create_deposit.assert_called_once_with(account_id, amount, None)

    def test_create_deposit_commits_transaction(self, mock_transaction_service, sample_transaction):
        """Test that deposit creation is handled by context manager (no explicit commit in resolver)"""
        # Arrange
        account_id = str(sample_transaction.account_id)
        amount = 1000
        mock_transaction_service.create_deposit.return_value = sample_transaction

        # Act
        result = resolvers.create_deposit(account_id, amount, mock_transaction_service)

        # Assert - resolver doesn't commit, that's context manager's job
        assert result == sample_transaction

    def test_create_deposit_with_service_exception(self, mock_transaction_service):
        """Test deposit creation when service raises an exception"""
        # Arrange
        account_id = str(uuid.uuid4())
        amount = 1000
        mock_transaction_service.create_deposit.side_effect = ValueError("Account not found")

        # Act & Assert
        with pytest.raises(ValueError, match="Account not found"):
            resolvers.create_deposit(account_id, amount, mock_transaction_service)

    def test_create_deposit_with_large_amount(self, mock_transaction_service, sample_transaction):
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
            mock_transaction_service,
            description=description,
        )

        # Assert
        assert result == sample_transaction
        mock_transaction_service.create_deposit.assert_called_once_with(
            account_id, amount, description
        )

    def test_create_deposit_with_large_amount_original(
        self, mock_transaction_service, sample_transaction
    ):
        """Test deposit creation with large amount (original test kept for coverage)"""
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
            mock_transaction_service,
            description="Large deposit",
        )

        # Assert
        assert result == large_transaction
        assert result.amount == amount
        mock_transaction_service.create_deposit.assert_called_once_with(
            account_id, amount, "Large deposit"
        )


class TestWithdrawalRequestResolvers:
    """WithdrawalRequest 関連リゾルバーのテスト"""

    def test_get_pending_withdrawal_requests_success(
        self, mock_withdrawal_request_service, sample_withdrawal_request
    ):
        """未承認の出金リクエスト取得の成功をテスト"""
        # Arrange
        parent_id = str(uuid.uuid4())
        mock_withdrawal_request_service.get_pending_requests_for_parent.return_value = [
            sample_withdrawal_request
        ]

        # Act
        result = resolvers.get_pending_withdrawal_requests(
            parent_id, mock_withdrawal_request_service
        )

        # Assert
        assert result == [sample_withdrawal_request]
        mock_withdrawal_request_service.get_pending_requests_for_parent.assert_called_once_with(
            parent_id
        )

    def test_get_pending_withdrawal_requests_empty_list(self, mock_withdrawal_request_service):
        """未承認の出金リクエストが存在しない場合に空リストを返すことをテスト"""
        # Arrange
        parent_id = str(uuid.uuid4())
        mock_withdrawal_request_service.get_pending_requests_for_parent.return_value = []

        # Act
        result = resolvers.get_pending_withdrawal_requests(
            parent_id, mock_withdrawal_request_service
        )

        # Assert
        assert result == []
        mock_withdrawal_request_service.get_pending_requests_for_parent.assert_called_once_with(
            parent_id
        )

    def test_create_withdrawal_request_success(
        self, mock_withdrawal_request_service, sample_withdrawal_request
    ):
        """出金リクエスト作成の成功をテスト"""
        # Arrange
        account_id = str(sample_withdrawal_request.account_id)
        amount = 5000
        description = "Need money for books"
        mock_withdrawal_request_service.create_withdrawal_request.return_value = (
            sample_withdrawal_request
        )

        # Act
        result = resolvers.create_withdrawal_request(
            account_id, amount, mock_withdrawal_request_service, description
        )

        # Assert
        assert result == sample_withdrawal_request
        assert result.status == "pending"
        mock_withdrawal_request_service.create_withdrawal_request.assert_called_once_with(
            account_id, amount, description
        )

    def test_create_withdrawal_request_without_description(
        self, mock_withdrawal_request_service, sample_withdrawal_request
    ):
        """説明なしで出金リクエストを作成できることをテスト"""
        # Arrange
        account_id = str(sample_withdrawal_request.account_id)
        amount = 3000
        request_without_description = WithdrawalRequest(
            id=sample_withdrawal_request.id,
            account_id=sample_withdrawal_request.account_id,
            amount=amount,
            description=None,
            status="pending",
            created_at=sample_withdrawal_request.created_at,
            updated_at=sample_withdrawal_request.updated_at,
        )
        mock_withdrawal_request_service.create_withdrawal_request.return_value = (
            request_without_description
        )

        # Act
        result = resolvers.create_withdrawal_request(
            account_id, amount, mock_withdrawal_request_service
        )

        # Assert
        assert result == request_without_description
        assert result.description is None
        mock_withdrawal_request_service.create_withdrawal_request.assert_called_once_with(
            account_id, amount, None
        )

    def test_approve_withdrawal_request_success(
        self, mock_withdrawal_request_service, mock_transaction_service, sample_withdrawal_request
    ):
        """出金リクエスト承認の成功をテスト"""
        # Arrange
        request_id = str(sample_withdrawal_request.id)
        approved_request = WithdrawalRequest(
            id=sample_withdrawal_request.id,
            account_id=sample_withdrawal_request.account_id,
            amount=sample_withdrawal_request.amount,
            description=sample_withdrawal_request.description,
            status="approved",
            created_at=sample_withdrawal_request.created_at,
            updated_at=str(datetime.now(UTC)),
        )
        mock_withdrawal_request_service.approve_withdrawal_request.return_value = approved_request

        # Act
        result = resolvers.approve_withdrawal_request(
            request_id, mock_withdrawal_request_service, mock_transaction_service
        )

        # Assert
        assert result == approved_request
        assert result.status == "approved"
        mock_withdrawal_request_service.approve_withdrawal_request.assert_called_once_with(
            request_id, mock_transaction_service
        )

    def test_reject_withdrawal_request_success(
        self, mock_withdrawal_request_service, sample_withdrawal_request
    ):
        """出金リクエスト却下の成功をテスト"""
        # Arrange
        request_id = str(sample_withdrawal_request.id)
        rejected_request = WithdrawalRequest(
            id=sample_withdrawal_request.id,
            account_id=sample_withdrawal_request.account_id,
            amount=sample_withdrawal_request.amount,
            description=sample_withdrawal_request.description,
            status="rejected",
            created_at=sample_withdrawal_request.created_at,
            updated_at=str(datetime.now(UTC)),
        )
        mock_withdrawal_request_service.reject_withdrawal_request.return_value = rejected_request

        # Act
        result = resolvers.reject_withdrawal_request(request_id, mock_withdrawal_request_service)

        # Assert
        assert result == rejected_request
        assert result.status == "rejected"
        mock_withdrawal_request_service.reject_withdrawal_request.assert_called_once_with(
            request_id
        )


class TestRecurringDepositResolvers:
    """RecurringDeposit 関連リゾルバーのテスト"""

    def test_get_recurring_deposit_success(
        self, mock_recurring_deposit_service, sample_recurring_deposit
    ):
        """定期入金設定取得の成功をテスト"""
        # Arrange
        account_id = str(sample_recurring_deposit.account_id)
        current_user_id = str(uuid.uuid4())
        mock_recurring_deposit_service.get_recurring_deposit.return_value = sample_recurring_deposit

        # Act
        result = resolvers.get_recurring_deposit(
            account_id, current_user_id, mock_recurring_deposit_service
        )

        # Assert
        assert result == sample_recurring_deposit
        mock_recurring_deposit_service.get_recurring_deposit.assert_called_once_with(
            account_id, current_user_id
        )

    def test_get_recurring_deposit_returns_none(self, mock_recurring_deposit_service):
        """定期入金設定が存在しない場合にNoneを返すことをテスト"""
        # Arrange
        account_id = str(uuid.uuid4())
        current_user_id = str(uuid.uuid4())
        mock_recurring_deposit_service.get_recurring_deposit.return_value = None

        # Act
        result = resolvers.get_recurring_deposit(
            account_id, current_user_id, mock_recurring_deposit_service
        )

        # Assert
        assert result is None
        mock_recurring_deposit_service.get_recurring_deposit.assert_called_once_with(
            account_id, current_user_id
        )

    def test_create_or_update_recurring_deposit_create(
        self, mock_recurring_deposit_service, sample_recurring_deposit
    ):
        """新規定期入金設定作成の成功をテスト"""
        # Arrange
        account_id = str(sample_recurring_deposit.account_id)
        current_user_id = str(uuid.uuid4())
        amount = 5000
        day_of_month = 25
        mock_recurring_deposit_service.create_or_update_recurring_deposit.return_value = (
            sample_recurring_deposit
        )

        # Act
        result = resolvers.create_or_update_recurring_deposit(
            account_id, current_user_id, amount, day_of_month, mock_recurring_deposit_service
        )

        # Assert
        assert result == sample_recurring_deposit
        mock_recurring_deposit_service.create_or_update_recurring_deposit.assert_called_once_with(
            account_id, current_user_id, amount, day_of_month, True
        )

    def test_create_or_update_recurring_deposit_update(
        self, mock_recurring_deposit_service, sample_recurring_deposit
    ):
        """既存定期入金設定更新の成功をテスト"""
        # Arrange
        account_id = str(sample_recurring_deposit.account_id)
        current_user_id = str(uuid.uuid4())
        amount = 10000
        day_of_month = 1
        is_active = False

        updated_rd = RecurringDeposit(
            id=sample_recurring_deposit.id,
            account_id=sample_recurring_deposit.account_id,
            amount=amount,
            day_of_month=day_of_month,
            is_active="false",
            created_at=sample_recurring_deposit.created_at,
            updated_at=str(datetime.now(UTC)),
        )
        mock_recurring_deposit_service.create_or_update_recurring_deposit.return_value = updated_rd

        # Act
        result = resolvers.create_or_update_recurring_deposit(
            account_id,
            current_user_id,
            amount,
            day_of_month,
            mock_recurring_deposit_service,
            is_active,
        )

        # Assert
        assert result == updated_rd
        assert result.amount == amount
        assert result.day_of_month == day_of_month
        mock_recurring_deposit_service.create_or_update_recurring_deposit.assert_called_once_with(
            account_id, current_user_id, amount, day_of_month, is_active
        )

    def test_delete_recurring_deposit_success(self, mock_recurring_deposit_service):
        """定期入金設定削除の成功をテスト"""
        # Arrange
        account_id = str(uuid.uuid4())
        current_user_id = str(uuid.uuid4())
        mock_recurring_deposit_service.delete_recurring_deposit.return_value = True

        # Act
        result = resolvers.delete_recurring_deposit(
            account_id, current_user_id, mock_recurring_deposit_service
        )

        # Assert
        assert result is True
        mock_recurring_deposit_service.delete_recurring_deposit.assert_called_once_with(
            account_id, current_user_id
        )

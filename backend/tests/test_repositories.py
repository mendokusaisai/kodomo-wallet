"""Repository 実装のユニットテスト

Mock と SQLAlchemy の両方のリポジトリ実装をテスト
"""

import uuid
from datetime import UTC, datetime

import pytest

from app.repositories.mock_repositories import (
    MockAccountRepository,
    MockProfileRepository,
    MockRecurringDepositRepository,
    MockTransactionRepository,
    MockWithdrawalRequestRepository,
)
from app.repositories.sqlalchemy import (
    SQLAlchemyAccountRepository,
    SQLAlchemyProfileRepository,
    SQLAlchemyRecurringDepositRepository,
    SQLAlchemyTransactionRepository,
    SQLAlchemyWithdrawalRequestRepository,
)
from app.repositories.sqlalchemy.models import Account, Profile

# ============================================================================
# Fixtures
# ============================================================================


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
def sample_account(sample_profile):
    """テスト用のサンプルアカウントを作成"""
    return Account(
        id=uuid.uuid4(),
        user_id=sample_profile.id,
        balance=10000,
        currency="JPY",
        created_at=str(datetime.now(UTC)),
        updated_at=str(datetime.now(UTC)),
    )


# ============================================================================
# MockProfileRepository Tests
# ============================================================================


class TestMockProfileRepository:
    """MockProfileRepository のテストスイート"""

    def test_get_by_id_returns_none_when_not_found(self):
        """プロフィールが存在しない場合 get_by_id が None を返すことをテスト"""
        repo = MockProfileRepository()
        result = repo.get_by_id("non-existent-id")
        assert result is None

    def test_add_and_get_profile(self, sample_profile):
        """プロフィールの追加と取得をテスト"""
        repo = MockProfileRepository()
        repo.add(sample_profile)

        result = repo.get_by_id(str(sample_profile.id))
        assert result is not None
        assert result.id == sample_profile.id
        assert str(result.name) == "Test User"
        assert str(result.role) == "parent"

    def test_multiple_profiles(self):
        """複数のプロフィールの保存をテスト"""
        repo = MockProfileRepository()
        profile1 = Profile(
            id=uuid.uuid4(),
            name="User One",
            role="parent",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        profile2 = Profile(
            id=uuid.uuid4(),
            name="User Two",
            role="child",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )

        repo.add(profile1)
        repo.add(profile2)

        assert repo.get_by_id(str(profile1.id)) is not None
        assert repo.get_by_id(str(profile2.id)) is not None
        assert repo.get_by_id(str(profile1.id)).name == "User One"  # type: ignore[union-attr]
        assert repo.get_by_id(str(profile2.id)).name == "User Two"  # type: ignore[union-attr]


# ============================================================================
# MockAccountRepository Tests
# ============================================================================


class TestMockAccountRepository:
    """MockAccountRepository のテストスイート"""

    def test_get_by_id_returns_none_when_not_found(self):
        """アカウントが存在しない場合 get_by_id が None を返すことをテスト"""
        repo = MockAccountRepository()
        result = repo.get_by_id("non-existent-id")
        assert result is None

    def test_add_and_get_account(self, sample_account):
        """アカウントの追加と取得をテスト"""
        repo = MockAccountRepository()
        repo.add(sample_account)

        result = repo.get_by_id(str(sample_account.id))
        assert result is not None
        assert result.id == sample_account.id
        assert int(result.balance) == 10000  # type: ignore[arg-type]
        assert str(result.currency) == "JPY"

    def test_get_by_user_id(self, sample_profile):
        """ユーザーのすべてのアカウント取得をテスト"""
        repo = MockAccountRepository()
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

        repo.add(account1)
        repo.add(account2)

        results = repo.get_by_user_id(str(sample_profile.id))
        assert len(results) == 2
        assert all(str(acc.user_id) == str(sample_profile.id) for acc in results)

    def test_get_by_user_id_empty_list(self):
        """Test that get_by_user_id returns empty list when no accounts exist"""
        repo = MockAccountRepository()
        results = repo.get_by_user_id("non-existent-user")
        assert results == []

    def test_update_balance(self, sample_account):
        """Test updating account balance"""
        repo = MockAccountRepository()
        repo.add(sample_account)

        repo.update_balance(sample_account, 15000)

        result = repo.get_by_id(str(sample_account.id))
        assert result is not None
        assert int(result.balance) == 15000  # type: ignore[arg-type]


# ============================================================================
# MockTransactionRepository Tests
# ============================================================================


class TestMockTransactionRepository:
    """Test suite for MockTransactionRepository"""

    def test_create_transaction(self, sample_account):
        """Test creating a transaction"""
        repo = MockTransactionRepository()
        created_at = datetime.now(UTC)

        transaction = repo.create(
            account_id=str(sample_account.id),
            transaction_type="deposit",
            amount=5000,
            description="Test deposit",
            created_at=created_at,
        )

        assert transaction.id is not None
        assert str(transaction.account_id) == str(sample_account.id)
        assert str(transaction.type) == "deposit"
        assert int(transaction.amount) == 5000  # type: ignore[arg-type]
        assert str(transaction.description) == "Test deposit"

    def test_get_by_account_id(self, sample_account):
        """Test retrieving transactions by account ID"""
        repo = MockTransactionRepository()

        # Create multiple transactions
        repo.create(
            account_id=str(sample_account.id),
            transaction_type="deposit",
            amount=1000,
            description="Deposit 1",
            created_at=datetime.now(UTC),
        )
        repo.create(
            account_id=str(sample_account.id),
            transaction_type="withdraw",
            amount=500,
            description="Withdraw 1",
            created_at=datetime.now(UTC),
        )

        results = repo.get_by_account_id(str(sample_account.id))
        assert len(results) == 2
        assert all(str(t.account_id) == str(sample_account.id) for t in results)

    def test_get_by_account_id_with_limit(self, sample_account):
        """Test that limit parameter works correctly"""
        repo = MockTransactionRepository()

        # Create 5 transactions
        for i in range(5):
            repo.create(
                account_id=str(sample_account.id),
                transaction_type="deposit",
                amount=1000 * (i + 1),
                description=f"Transaction {i + 1}",
                created_at=datetime.now(UTC),
            )

        results = repo.get_by_account_id(str(sample_account.id), limit=3)
        assert len(results) == 3

    def test_get_by_account_id_sorted_by_date(self, sample_account):
        """Test that transactions are sorted by created_at descending"""
        repo = MockTransactionRepository()

        # Create transactions with different timestamps
        from datetime import timedelta

        base_time = datetime.now(UTC)
        t1 = repo.create(
            account_id=str(sample_account.id),
            transaction_type="deposit",
            amount=1000,
            description="First",
            created_at=base_time,
        )
        t2 = repo.create(
            account_id=str(sample_account.id),
            transaction_type="deposit",
            amount=2000,
            description="Second",
            created_at=base_time + timedelta(seconds=1),
        )
        t3 = repo.create(
            account_id=str(sample_account.id),
            transaction_type="deposit",
            amount=3000,
            description="Third",
            created_at=base_time + timedelta(seconds=2),
        )

        results = repo.get_by_account_id(str(sample_account.id))

        # Should be in descending order (newest first)
        assert results[0].id == t3.id
        assert results[1].id == t2.id
        assert results[2].id == t1.id


# ============================================================================
# SQLAlchemyProfileRepository Tests
# ============================================================================


class TestSQLAlchemyProfileRepository:
    """Test suite for SQLAlchemyProfileRepository"""

    def test_get_by_id_returns_none_when_not_found(self, in_memory_db):
        """Test that get_by_id returns None when profile doesn't exist"""
        repo = SQLAlchemyProfileRepository(in_memory_db)
        result = repo.get_by_id(str(uuid.uuid4()))
        assert result is None

    def test_add_and_get_profile(self, in_memory_db, sample_profile):
        """Test adding a profile and retrieving it"""
        in_memory_db.add(sample_profile)
        in_memory_db.commit()

        repo = SQLAlchemyProfileRepository(in_memory_db)
        result = repo.get_by_id(str(sample_profile.id))

        assert result is not None
        assert result.id == sample_profile.id
        assert str(result.name) == "Test User"
        assert str(result.role) == "parent"


# ============================================================================
# SQLAlchemyAccountRepository Tests
# ============================================================================


class TestSQLAlchemyAccountRepository:
    """Test suite for SQLAlchemyAccountRepository"""

    def test_get_by_id_returns_none_when_not_found(self, in_memory_db):
        """Test that get_by_id returns None when account doesn't exist"""
        repo = SQLAlchemyAccountRepository(in_memory_db)
        result = repo.get_by_id(str(uuid.uuid4()))
        assert result is None

    def test_add_and_get_account(self, in_memory_db, sample_profile, sample_account):
        """Test adding an account and retrieving it"""
        in_memory_db.add(sample_profile)
        in_memory_db.add(sample_account)
        in_memory_db.commit()

        repo = SQLAlchemyAccountRepository(in_memory_db)
        result = repo.get_by_id(str(sample_account.id))

        assert result is not None
        assert result.id == sample_account.id
        assert int(result.balance) == 10000  # type: ignore[arg-type]

    def test_get_by_user_id(self, in_memory_db, sample_profile):
        """Test retrieving all accounts for a user"""
        account1 = Account(
            id=uuid.uuid4(),
            user_id=sample_profile.id,
            balance=5000,
            currency="JPY",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        account2 = Account(
            id=uuid.uuid4(),
            user_id=sample_profile.id,
            balance=3000,
            currency="JPY",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        in_memory_db.add(sample_profile)
        in_memory_db.add(account1)
        in_memory_db.add(account2)
        in_memory_db.commit()

        repo = SQLAlchemyAccountRepository(in_memory_db)
        results = repo.get_by_user_id(str(sample_profile.id))

        assert len(results) == 2
        assert all(str(acc.user_id) == str(sample_profile.id) for acc in results)

    def test_update_balance(self, in_memory_db, sample_profile, sample_account):
        """Test updating account balance"""
        in_memory_db.add(sample_profile)
        in_memory_db.add(sample_account)
        in_memory_db.commit()

        repo = SQLAlchemyAccountRepository(in_memory_db)
        account = repo.get_by_id(str(sample_account.id))
        assert account is not None

        repo.update_balance(account, 15000)
        in_memory_db.commit()

        # Verify the balance was updated
        result = repo.get_by_id(str(sample_account.id))
        assert result is not None
        assert int(result.balance) == 15000  # type: ignore[arg-type]


# ============================================================================
# SQLAlchemyTransactionRepository Tests
# ============================================================================


class TestSQLAlchemyTransactionRepository:
    """Test suite for SQLAlchemyTransactionRepository"""

    def test_create_transaction(self, in_memory_db, sample_profile, sample_account):
        """Test creating a transaction"""
        in_memory_db.add(sample_profile)
        in_memory_db.add(sample_account)
        in_memory_db.commit()

        repo = SQLAlchemyTransactionRepository(in_memory_db)
        created_at = datetime.now(UTC)

        transaction = repo.create(
            account_id=str(sample_account.id),
            transaction_type="deposit",
            amount=5000,
            description="Test deposit",
            created_at=created_at,
        )

        assert transaction.id is not None
        assert str(transaction.account_id) == str(sample_account.id)
        assert str(transaction.type) == "deposit"
        assert int(transaction.amount) == 5000  # type: ignore[arg-type]

    def test_get_by_account_id(self, in_memory_db, sample_profile, sample_account):
        """Test retrieving transactions by account ID"""
        in_memory_db.add(sample_profile)
        in_memory_db.add(sample_account)
        in_memory_db.commit()

        repo = SQLAlchemyTransactionRepository(in_memory_db)

        # Create transactions
        repo.create(
            account_id=str(sample_account.id),
            transaction_type="deposit",
            amount=1000,
            description="Deposit 1",
            created_at=datetime.now(UTC),
        )
        repo.create(
            account_id=str(sample_account.id),
            transaction_type="withdraw",
            amount=500,
            description="Withdraw 1",
            created_at=datetime.now(UTC),
        )
        in_memory_db.commit()

        results = repo.get_by_account_id(str(sample_account.id))
        assert len(results) == 2

    def test_get_by_account_id_with_limit(self, in_memory_db, sample_profile, sample_account):
        """Test that limit parameter works correctly"""
        in_memory_db.add(sample_profile)
        in_memory_db.add(sample_account)
        in_memory_db.commit()

        repo = SQLAlchemyTransactionRepository(in_memory_db)

        # Create 5 transactions
        for i in range(5):
            repo.create(
                account_id=str(sample_account.id),
                transaction_type="deposit",
                amount=1000 * (i + 1),
                description=f"Transaction {i + 1}",
                created_at=datetime.now(UTC),
            )
        in_memory_db.commit()

        results = repo.get_by_account_id(str(sample_account.id), limit=3)
        assert len(results) == 3


# ============================================================================
# MockWithdrawalRequestRepository Tests
# ============================================================================


class TestMockWithdrawalRequestRepository:
    """MockWithdrawalRequestRepository のテストスイート"""

    def test_create_withdrawal_request(self, sample_account):
        """出金リクエストの作成をテスト"""
        repo = MockWithdrawalRequestRepository()
        created_at = datetime.now(UTC)

        wr = repo.create(
            account_id=str(sample_account.id),
            amount=3000,
            description="Test withdrawal",
            created_at=created_at,
        )

        assert wr.id is not None
        assert str(wr.account_id) == str(sample_account.id)
        assert int(wr.amount) == 3000  # type: ignore[arg-type]
        assert str(wr.status) == "pending"
        assert str(wr.description) == "Test withdrawal"

    def test_get_by_id(self, sample_account):
        """ID による出金リクエスト取得をテスト"""
        repo = MockWithdrawalRequestRepository()
        wr = repo.create(
            account_id=str(sample_account.id),
            amount=2000,
            description="Snacks",
            created_at=datetime.now(UTC),
        )

        result = repo.get_by_id(str(wr.id))
        assert result is not None
        assert str(result.id) == str(wr.id)

    def test_get_by_id_returns_none_when_not_found(self):
        """存在しない ID で None を返すことをテスト"""
        repo = MockWithdrawalRequestRepository()
        result = repo.get_by_id("non-existent-id")
        assert result is None

    def test_get_pending_by_parent(self, sample_account):
        """保留中の出金リクエスト取得をテスト"""
        repo = MockWithdrawalRequestRepository()

        # pendingを2件作成
        wr1 = repo.create(
            account_id=str(sample_account.id),
            amount=1000,
            description="Request 1",
            created_at=datetime.now(UTC),
        )
        wr2 = repo.create(
            account_id=str(sample_account.id),
            amount=1500,
            description="Request 2",
            created_at=datetime.now(UTC),
        )

        # 1件をapprovedに変更
        repo.update_status(wr1, "approved", datetime.now(UTC))

        # pendingのみ取得（parent_idは簡略化実装のため任意）
        results = repo.get_pending_by_parent("any-parent-id")
        assert len(results) == 1
        assert str(results[0].id) == str(wr2.id)
        assert str(results[0].status) == "pending"

    def test_update_status(self, sample_account):
        """ステータス更新をテスト"""
        repo = MockWithdrawalRequestRepository()
        wr = repo.create(
            account_id=str(sample_account.id),
            amount=2000,
            description="Test",
            created_at=datetime.now(UTC),
        )

        updated_wr = repo.update_status(wr, "approved", datetime.now(UTC))
        assert str(updated_wr.status) == "approved"

        # リポジトリから再取得して確認
        result = repo.get_by_id(str(wr.id))
        assert result is not None
        assert str(result.status) == "approved"


# ============================================================================
# SQLAlchemyWithdrawalRequestRepository Tests
# ============================================================================


class TestSQLAlchemyWithdrawalRequestRepository:
    """SQLAlchemyWithdrawalRequestRepository のテストスイート"""

    def test_create_withdrawal_request(self, in_memory_db, sample_profile, sample_account):
        """出金リクエストの作成をテスト"""
        in_memory_db.add(sample_profile)
        in_memory_db.add(sample_account)
        in_memory_db.commit()

        repo = SQLAlchemyWithdrawalRequestRepository(in_memory_db)
        created_at = datetime.now(UTC)

        wr = repo.create(
            account_id=str(sample_account.id),
            amount=3000,
            description="Test withdrawal",
            created_at=created_at,
        )

        assert wr.id is not None
        assert str(wr.account_id) == str(sample_account.id)
        assert int(wr.amount) == 3000  # type: ignore[arg-type]
        assert str(wr.status) == "pending"

    def test_get_by_id(self, in_memory_db, sample_profile, sample_account):
        """ID による出金リクエスト取得をテスト"""
        in_memory_db.add(sample_profile)
        in_memory_db.add(sample_account)
        in_memory_db.commit()

        repo = SQLAlchemyWithdrawalRequestRepository(in_memory_db)
        wr = repo.create(
            account_id=str(sample_account.id),
            amount=2000,
            description="Snacks",
            created_at=datetime.now(UTC),
        )
        in_memory_db.commit()

        result = repo.get_by_id(str(wr.id))
        assert result is not None
        assert str(result.id) == str(wr.id)

    def test_get_by_id_returns_none_when_not_found(self, in_memory_db):
        """存在しない ID で None を返すことをテスト"""
        repo = SQLAlchemyWithdrawalRequestRepository(in_memory_db)
        result = repo.get_by_id(str(uuid.uuid4()))
        assert result is None

    def test_get_pending_by_parent(self, in_memory_db):
        """親の子に対する保留中の出金リクエスト取得をテスト"""
        # 親、子、アカウントを作成
        parent = Profile(
            id=uuid.uuid4(),
            name="Parent",
            role="parent",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        child = Profile(
            id=uuid.uuid4(),
            name="Child",
            role="child",
            parent_id=parent.id,
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        from app.repositories.sqlalchemy.models import Account

        account = Account(
            id=uuid.uuid4(),
            user_id=child.id,
            balance=10000,
            currency="JPY",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add_all([parent, child, account])
        in_memory_db.commit()

        repo = SQLAlchemyWithdrawalRequestRepository(in_memory_db)

        # pendingを2件、approvedを1件作成
        wr1 = repo.create(
            account_id=str(account.id),
            amount=1000,
            description="Request 1",
            created_at=datetime.now(UTC),
        )
        wr2 = repo.create(
            account_id=str(account.id),
            amount=1500,
            description="Request 2",
            created_at=datetime.now(UTC),
        )
        wr3 = repo.create(
            account_id=str(account.id),
            amount=2000,
            description="Request 3",
            created_at=datetime.now(UTC),
        )
        in_memory_db.commit()

        # 1件をapprovedに
        repo.update_status(wr1, "approved", datetime.now(UTC))
        in_memory_db.commit()

        # pendingのみ取得
        results = repo.get_pending_by_parent(str(parent.id))
        assert len(results) == 2
        result_ids = {str(r.id) for r in results}
        assert str(wr2.id) in result_ids
        assert str(wr3.id) in result_ids

    def test_update_status(self, in_memory_db, sample_profile, sample_account):
        """ステータス更新をテスト"""
        in_memory_db.add(sample_profile)
        in_memory_db.add(sample_account)
        in_memory_db.commit()

        repo = SQLAlchemyWithdrawalRequestRepository(in_memory_db)
        wr = repo.create(
            account_id=str(sample_account.id),
            amount=2000,
            description="Test",
            created_at=datetime.now(UTC),
        )
        in_memory_db.commit()

        updated_wr = repo.update_status(wr, "rejected", datetime.now(UTC))
        in_memory_db.commit()

        assert str(updated_wr.status) == "rejected"

        # リポジトリから再取得して確認
        result = repo.get_by_id(str(wr.id))
        assert result is not None
        assert str(result.status) == "rejected"


class TestMockRecurringDepositRepository:
    """MockRecurringDepositRepository のテスト"""

    def test_create_recurring_deposit(self):
        """定期入金設定を作成できることをテスト"""
        repo = MockRecurringDepositRepository()
        account_id = str(uuid.uuid4())

        rd = repo.create(
            account_id=account_id,
            amount=5000,
            day_of_month=15,
            created_at=datetime.now(UTC),
        )

        assert rd is not None
        assert str(rd.account_id) == account_id
        assert rd.amount == 5000
        assert rd.day_of_month == 15
        assert rd.is_active is True

    def test_get_by_account_id(self):
        """account_idで定期入金設定を取得できることをテスト"""
        repo = MockRecurringDepositRepository()
        account_id = str(uuid.uuid4())

        # 作成
        rd = repo.create(
            account_id=account_id,
            amount=3000,
            day_of_month=1,
            created_at=datetime.now(UTC),
        )

        # 取得
        result = repo.get_by_account_id(account_id)
        assert result is not None
        assert result.id == rd.id
        assert result.amount == 3000

    def test_get_by_account_id_returns_none_when_not_found(self):
        """存在しないaccount_idの場合Noneを返すことをテスト"""
        repo = MockRecurringDepositRepository()
        account_id = str(uuid.uuid4())

        result = repo.get_by_account_id(account_id)
        assert result is None

    def test_update_recurring_deposit(self):
        """定期入金設定を更新できることをテスト"""
        repo = MockRecurringDepositRepository()
        account_id = str(uuid.uuid4())

        # 作成
        rd = repo.create(
            account_id=account_id,
            amount=5000,
            day_of_month=15,
            created_at=datetime.now(UTC),
        )

        # 更新
        updated_rd = repo.update(
            rd,
            amount=10000,
            day_of_month=25,
            is_active=False,
            updated_at=datetime.now(UTC),
        )

        assert updated_rd.amount == 10000
        assert updated_rd.day_of_month == 25
        assert updated_rd.is_active is False

    def test_delete_recurring_deposit(self):
        """定期入金設定を削除できることをテスト"""
        repo = MockRecurringDepositRepository()
        account_id = str(uuid.uuid4())

        # 作成
        rd = repo.create(
            account_id=account_id,
            amount=5000,
            day_of_month=15,
            created_at=datetime.now(UTC),
        )

        # 削除
        result = repo.delete(rd)
        assert result is True

        # 削除後は取得できない
        assert repo.get_by_account_id(account_id) is None


class TestSQLAlchemyRecurringDepositRepository:
    """SQLAlchemyRecurringDepositRepository のテスト"""

    def test_create_recurring_deposit(self, in_memory_db):
        """定期入金設定を作成できることをテスト"""
        # プロフィールとアカウントを作成
        profile = Profile(
            id=uuid.uuid4(),
            name="Parent",
            role="parent",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        account = Account(
            id=uuid.uuid4(),
            user_id=profile.id,
            balance=0,
            currency="JPY",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add_all([profile, account])
        in_memory_db.commit()

        # 定期入金設定を作成
        repo = SQLAlchemyRecurringDepositRepository(in_memory_db)
        rd = repo.create(
            account_id=str(account.id),
            amount=5000,
            day_of_month=15,
            created_at=datetime.now(UTC),
        )
        in_memory_db.commit()

        assert rd is not None
        assert str(rd.account_id) == str(account.id)
        assert rd.amount == 5000
        assert rd.day_of_month == 15

    def test_get_by_account_id(self, in_memory_db):
        """account_idで定期入金設定を取得できることをテスト"""
        # プロフィールとアカウントを作成
        profile = Profile(
            id=uuid.uuid4(),
            name="Parent",
            role="parent",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        account = Account(
            id=uuid.uuid4(),
            user_id=profile.id,
            balance=0,
            currency="JPY",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add_all([profile, account])
        in_memory_db.commit()

        # 定期入金設定を作成
        repo = SQLAlchemyRecurringDepositRepository(in_memory_db)
        rd = repo.create(
            account_id=str(account.id),
            amount=3000,
            day_of_month=1,
            created_at=datetime.now(UTC),
        )
        in_memory_db.commit()

        # 取得
        result = repo.get_by_account_id(str(account.id))
        assert result is not None
        assert str(result.id) == str(rd.id)
        assert result.amount == 3000

    def test_get_by_account_id_returns_none_when_not_found(self, in_memory_db):
        """存在しないaccount_idの場合Noneを返すことをテスト"""
        repo = SQLAlchemyRecurringDepositRepository(in_memory_db)
        account_id = str(uuid.uuid4())

        result = repo.get_by_account_id(account_id)
        assert result is None

    def test_update_recurring_deposit(self, in_memory_db):
        """定期入金設定を更新できることをテスト"""
        # プロフィールとアカウントを作成
        profile = Profile(
            id=uuid.uuid4(),
            name="Parent",
            role="parent",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        account = Account(
            id=uuid.uuid4(),
            user_id=profile.id,
            balance=0,
            currency="JPY",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add_all([profile, account])
        in_memory_db.commit()

        # 定期入金設定を作成
        repo = SQLAlchemyRecurringDepositRepository(in_memory_db)
        rd = repo.create(
            account_id=str(account.id),
            amount=5000,
            day_of_month=15,
            created_at=datetime.now(UTC),
        )
        in_memory_db.commit()

        # 更新
        updated_rd = repo.update(
            rd,
            amount=10000,
            day_of_month=25,
            is_active=False,
            updated_at=datetime.now(UTC),
        )
        in_memory_db.commit()

        assert updated_rd.amount == 10000
        assert updated_rd.day_of_month == 25
        assert str(updated_rd.is_active) == "false"

    def test_delete_recurring_deposit(self, in_memory_db):
        """定期入金設定を削除できることをテスト"""
        # プロフィールとアカウントを作成
        profile = Profile(
            id=uuid.uuid4(),
            name="Parent",
            role="parent",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        account = Account(
            id=uuid.uuid4(),
            user_id=profile.id,
            balance=0,
            currency="JPY",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add_all([profile, account])
        in_memory_db.commit()

        # 定期入金設定を作成
        repo = SQLAlchemyRecurringDepositRepository(in_memory_db)
        rd = repo.create(
            account_id=str(account.id),
            amount=5000,
            day_of_month=15,
            created_at=datetime.now(UTC),
        )
        in_memory_db.commit()

        # 削除
        result = repo.delete(rd)
        in_memory_db.commit()

        assert result is True

        # 削除後は取得できない
        assert repo.get_by_account_id(str(account.id)) is None

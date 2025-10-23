"""
Unit tests for Repository implementations.

Tests both Mock and SQLAlchemy repository implementations.
"""

import uuid
from datetime import UTC, datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.models import Account, Base, Profile
from app.repositories.mock_repositories import (
    MockAccountRepository,
    MockProfileRepository,
    MockTransactionRepository,
)
from app.repositories.sqlalchemy_repositories import (
    SQLAlchemyAccountRepository,
    SQLAlchemyProfileRepository,
    SQLAlchemyTransactionRepository,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def in_memory_db():
    """Create an in-memory SQLite database for testing"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


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
def sample_account(sample_profile):
    """Create a sample account for testing"""
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
    """Test suite for MockProfileRepository"""

    def test_get_by_id_returns_none_when_not_found(self):
        """Test that get_by_id returns None when profile doesn't exist"""
        repo = MockProfileRepository()
        result = repo.get_by_id("non-existent-id")
        assert result is None

    def test_add_and_get_profile(self, sample_profile):
        """Test adding a profile and retrieving it"""
        repo = MockProfileRepository()
        repo.add(sample_profile)

        result = repo.get_by_id(str(sample_profile.id))
        assert result is not None
        assert result.id == sample_profile.id
        assert str(result.name) == "Test User"
        assert str(result.role) == "parent"

    def test_multiple_profiles(self):
        """Test storing multiple profiles"""
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
    """Test suite for MockAccountRepository"""

    def test_get_by_id_returns_none_when_not_found(self):
        """Test that get_by_id returns None when account doesn't exist"""
        repo = MockAccountRepository()
        result = repo.get_by_id("non-existent-id")
        assert result is None

    def test_add_and_get_account(self, sample_account):
        """Test adding an account and retrieving it"""
        repo = MockAccountRepository()
        repo.add(sample_account)

        result = repo.get_by_id(str(sample_account.id))
        assert result is not None
        assert result.id == sample_account.id
        assert int(result.balance) == 10000  # type: ignore[arg-type]
        assert str(result.currency) == "JPY"

    def test_get_by_user_id(self, sample_profile):
        """Test retrieving all accounts for a user"""
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

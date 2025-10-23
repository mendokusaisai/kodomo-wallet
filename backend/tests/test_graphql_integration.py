"""Integration tests for GraphQL resolvers.

Tests resolver functions with database integration.
"""

import uuid
from datetime import UTC, datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.graphql import resolvers
from app.models.models import Account, Base, Profile, Transaction
from app.repositories.sqlalchemy_repositories import (
    SQLAlchemyAccountRepository,
    SQLAlchemyProfileRepository,
    SQLAlchemyTransactionRepository,
)
from app.services.business_services import (
    AccountService,
    ProfileService,
    TransactionService,
)


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
def services(in_memory_db: Session):
    """Create service instances with repositories"""
    profile_repo = SQLAlchemyProfileRepository(in_memory_db)
    account_repo = SQLAlchemyAccountRepository(in_memory_db)
    transaction_repo = SQLAlchemyTransactionRepository(in_memory_db)

    profile_service = ProfileService(profile_repo)
    account_service = AccountService(account_repo)
    transaction_service = TransactionService(transaction_repo, account_repo)

    return {
        "profile": profile_service,
        "account": account_service,
        "transaction": transaction_service,
    }


@pytest.fixture
def sample_data(in_memory_db: Session):
    """Create sample data for testing"""
    # Create profile
    profile = Profile(
        id=uuid.uuid4(),
        name="Test User",
        role="parent",
        created_at=str(datetime.now(UTC)),
        updated_at=str(datetime.now(UTC)),
    )
    in_memory_db.add(profile)

    # Create account
    account = Account(
        id=uuid.uuid4(),
        user_id=profile.id,
        balance=10000,
        currency="JPY",
        goal_name="Test Goal",
        goal_amount=50000,
        created_at=str(datetime.now(UTC)),
        updated_at=str(datetime.now(UTC)),
    )
    in_memory_db.add(account)

    # Create transaction
    transaction = Transaction(
        id=uuid.uuid4(),
        account_id=account.id,
        type="deposit",
        amount=5000,
        description="Initial deposit",
        created_at=str(datetime.now(UTC)),
    )
    in_memory_db.add(transaction)

    in_memory_db.commit()

    return {"profile": profile, "account": account, "transaction": transaction}


class TestResolverIntegration:
    """Test resolver functions with database integration"""

    def test_get_profile_by_id(self, sample_data, services):
        """Test getting profile by ID"""
        profile_id = str(sample_data["profile"].id)
        result = resolvers.get_profile_by_id(profile_id, services["profile"])

        assert result is not None
        assert result.id == sample_data["profile"].id
        assert result.name == "Test User"
        assert result.role == "parent"

    def test_get_profile_not_found(self, services):
        """Test getting non-existent profile returns None"""
        result = resolvers.get_profile_by_id(str(uuid.uuid4()), services["profile"])
        assert result is None

    def test_get_accounts_by_user_id(self, sample_data, services):
        """Test getting accounts for a user"""
        user_id = str(sample_data["profile"].id)
        results = resolvers.get_accounts_by_user_id(user_id, services["account"])

        assert len(results) == 1
        assert results[0].id == sample_data["account"].id
        assert results[0].balance == 10000
        assert results[0].currency == "JPY"

    def test_get_accounts_empty(self, services):
        """Test getting accounts for non-existent user"""
        results = resolvers.get_accounts_by_user_id(str(uuid.uuid4()), services["account"])
        assert results == []

    def test_get_transactions_by_account_id(self, sample_data, services):
        """Test getting transactions for an account"""
        account_id = str(sample_data["account"].id)
        results = resolvers.get_transactions_by_account_id(
            account_id, services["transaction"], limit=10
        )

        assert len(results) == 1
        assert results[0].type == "deposit"
        assert results[0].amount == 5000
        assert results[0].description == "Initial deposit"

    def test_get_transactions_empty(self, services):
        """Test getting transactions for non-existent account"""
        results = resolvers.get_transactions_by_account_id(
            str(uuid.uuid4()), services["transaction"], limit=10
        )
        assert results == []

    def test_create_deposit(self, in_memory_db, sample_data, services):
        """Test creating a deposit"""
        account_id = str(sample_data["account"].id)
        initial_balance = sample_data["account"].balance

        transaction = resolvers.create_deposit(
            account_id, 3000, in_memory_db, services["transaction"], "Test deposit"
        )

        assert transaction is not None
        assert transaction.type == "deposit"
        assert transaction.amount == 3000
        assert transaction.description == "Test deposit"

        # Verify balance was updated
        in_memory_db.refresh(sample_data["account"])
        assert sample_data["account"].balance == initial_balance + 3000

    def test_create_deposit_account_not_found(self, in_memory_db, services):
        """Test creating deposit for non-existent account"""
        with pytest.raises(Exception, match="Account .* not found"):
            resolvers.create_deposit(
                str(uuid.uuid4()), 1000, in_memory_db, services["transaction"], "Test"
            )

    def test_create_deposit_updates_transaction_list(self, in_memory_db, sample_data, services):
        """Test that deposit creates a queryable transaction"""
        account_id = str(sample_data["account"].id)

        # Create deposit
        resolvers.create_deposit(
            account_id, 2000, in_memory_db, services["transaction"], "New deposit"
        )

        # Query transactions
        transactions = resolvers.get_transactions_by_account_id(account_id, services["transaction"])

        # Should have 2 transactions now (initial + new)
        assert len(transactions) == 2

    def test_multiple_deposits(self, in_memory_db, sample_data, services):
        """Test creating multiple deposits"""
        account_id = str(sample_data["account"].id)
        initial_balance = sample_data["account"].balance

        resolvers.create_deposit(
            account_id, 1000, in_memory_db, services["transaction"], "Deposit 1"
        )
        resolvers.create_deposit(
            account_id, 2000, in_memory_db, services["transaction"], "Deposit 2"
        )
        resolvers.create_deposit(
            account_id, 3000, in_memory_db, services["transaction"], "Deposit 3"
        )

        # Verify final balance
        in_memory_db.refresh(sample_data["account"])
        assert sample_data["account"].balance == initial_balance + 6000

        # Verify transaction count
        transactions = resolvers.get_transactions_by_account_id(account_id, services["transaction"])
        assert len(transactions) == 4  # 1 initial + 3 new

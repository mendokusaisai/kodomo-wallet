"""Unit tests for SQLAlchemy models.

Tests database constraints, relationships, and model behavior.
"""

import uuid
from datetime import UTC, datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.models import Account, Base, Profile, Transaction


@pytest.fixture
def in_memory_db():
    """Create an in-memory SQLite database for testing"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestProfileModel:
    """Test suite for Profile model"""

    def test_create_parent_profile(self, in_memory_db):
        """Test creating a parent profile"""
        profile = Profile(
            id=uuid.uuid4(),
            name="Parent User",
            role="parent",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add(profile)
        in_memory_db.commit()

        result = in_memory_db.query(Profile).filter_by(id=profile.id).first()
        assert result is not None
        assert result.name == "Parent User"
        assert result.role == "parent"
        assert result.parent_id is None

    def test_create_child_profile_with_parent(self, in_memory_db):
        """Test creating a child profile with parent relationship"""
        parent = Profile(
            id=uuid.uuid4(),
            name="Parent",
            role="parent",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add(parent)
        in_memory_db.commit()

        child = Profile(
            id=uuid.uuid4(),
            name="Child",
            role="child",
            parent_id=parent.id,
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add(child)
        in_memory_db.commit()

        result = in_memory_db.query(Profile).filter_by(id=child.id).first()
        assert result is not None
        assert result.parent_id == parent.id

    def test_profile_with_avatar_url(self, in_memory_db):
        """Test profile with optional avatar URL"""
        profile = Profile(
            id=uuid.uuid4(),
            name="User",
            role="parent",
            avatar_url="https://example.com/avatar.jpg",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add(profile)
        in_memory_db.commit()

        result = in_memory_db.query(Profile).filter_by(id=profile.id).first()
        assert result is not None
        assert result.avatar_url == "https://example.com/avatar.jpg"


class TestAccountModel:
    """Test suite for Account model"""

    def test_create_account(self, in_memory_db):
        """Test creating an account"""
        profile = Profile(
            id=uuid.uuid4(),
            name="User",
            role="parent",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add(profile)
        in_memory_db.commit()

        account = Account(
            id=uuid.uuid4(),
            user_id=profile.id,
            balance=10000,
            currency="JPY",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add(account)
        in_memory_db.commit()

        result = in_memory_db.query(Account).filter_by(id=account.id).first()
        assert result is not None
        assert result.user_id == profile.id
        assert int(result.balance) == 10000
        assert result.currency == "JPY"

    def test_account_with_savings_goal(self, in_memory_db):
        """Test account with savings goal"""
        profile = Profile(
            id=uuid.uuid4(),
            name="Child",
            role="child",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add(profile)
        in_memory_db.commit()

        account = Account(
            id=uuid.uuid4(),
            user_id=profile.id,
            balance=5000,
            currency="JPY",
            goal_name="ゲーム機",
            goal_amount=30000,
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add(account)
        in_memory_db.commit()

        result = in_memory_db.query(Account).filter_by(id=account.id).first()
        assert result is not None
        assert result.goal_name == "ゲーム機"
        assert result.goal_amount == 30000

    def test_multiple_accounts_per_user(self, in_memory_db):
        """Test that a user can have multiple accounts"""
        profile = Profile(
            id=uuid.uuid4(),
            name="User",
            role="parent",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add(profile)
        in_memory_db.commit()

        account1 = Account(
            id=uuid.uuid4(),
            user_id=profile.id,
            balance=10000,
            currency="JPY",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        account2 = Account(
            id=uuid.uuid4(),
            user_id=profile.id,
            balance=5000,
            currency="JPY",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add_all([account1, account2])
        in_memory_db.commit()

        results = in_memory_db.query(Account).filter_by(user_id=profile.id).all()
        assert len(results) == 2


class TestTransactionModel:
    """Test suite for Transaction model"""

    def test_create_deposit_transaction(self, in_memory_db):
        """Test creating a deposit transaction"""
        # Create profile and account
        profile = Profile(
            id=uuid.uuid4(),
            name="User",
            role="parent",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        account = Account(
            id=uuid.uuid4(),
            user_id=profile.id,
            balance=10000,
            currency="JPY",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add_all([profile, account])
        in_memory_db.commit()

        # Create transaction
        transaction = Transaction(
            id=uuid.uuid4(),
            account_id=account.id,
            type="deposit",
            amount=5000,
            description="Test deposit",
            created_at=str(datetime.now(UTC)),
        )
        in_memory_db.add(transaction)
        in_memory_db.commit()

        result = in_memory_db.query(Transaction).filter_by(id=transaction.id).first()
        assert result is not None
        assert result.account_id == account.id
        assert result.type == "deposit"
        assert result.amount == 5000
        assert result.description == "Test deposit"

    def test_transaction_types(self, in_memory_db):
        """Test different transaction types"""
        profile = Profile(
            id=uuid.uuid4(),
            name="User",
            role="parent",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        account = Account(
            id=uuid.uuid4(),
            user_id=profile.id,
            balance=10000,
            currency="JPY",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add_all([profile, account])
        in_memory_db.commit()

        transaction_types = ["deposit", "withdraw", "reward"]
        for tx_type in transaction_types:
            transaction = Transaction(
                id=uuid.uuid4(),
                account_id=account.id,
                type=tx_type,
                amount=1000,
                description=f"Test {tx_type}",
                created_at=str(datetime.now(UTC)),
            )
            in_memory_db.add(transaction)

        in_memory_db.commit()

        results = in_memory_db.query(Transaction).filter_by(account_id=account.id).all()
        assert len(results) == 3
        types = {tx.type for tx in results}
        assert types == {"deposit", "withdraw", "reward"}

    def test_transaction_without_description(self, in_memory_db):
        """Test that transactions can be created without description"""
        profile = Profile(
            id=uuid.uuid4(),
            name="User",
            role="parent",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        account = Account(
            id=uuid.uuid4(),
            user_id=profile.id,
            balance=10000,
            currency="JPY",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add_all([profile, account])
        in_memory_db.commit()

        transaction = Transaction(
            id=uuid.uuid4(),
            account_id=account.id,
            type="deposit",
            amount=1000,
            created_at=str(datetime.now(UTC)),
        )
        in_memory_db.add(transaction)
        in_memory_db.commit()

        result = in_memory_db.query(Transaction).filter_by(id=transaction.id).first()
        assert result is not None
        assert result.description is None


class TestModelRelationships:
    """Test relationships between models"""

    def test_profile_to_accounts_relationship(self, in_memory_db):
        """Test that profile can access its accounts"""
        profile = Profile(
            id=uuid.uuid4(),
            name="User",
            role="parent",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add(profile)
        in_memory_db.commit()

        # Create multiple accounts
        for i in range(3):
            account = Account(
                id=uuid.uuid4(),
                user_id=profile.id,
                balance=10000 * (i + 1),
                currency="JPY",
                created_at=str(datetime.now(UTC)),
                updated_at=str(datetime.now(UTC)),
            )
            in_memory_db.add(account)
        in_memory_db.commit()

        # Query accounts through user_id
        accounts = in_memory_db.query(Account).filter_by(user_id=profile.id).all()
        assert len(accounts) == 3

    def test_account_to_transactions_relationship(self, in_memory_db):
        """Test that account can access its transactions"""
        profile = Profile(
            id=uuid.uuid4(),
            name="User",
            role="parent",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        account = Account(
            id=uuid.uuid4(),
            user_id=profile.id,
            balance=10000,
            currency="JPY",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add_all([profile, account])
        in_memory_db.commit()

        # Create multiple transactions
        for i in range(5):
            transaction = Transaction(
                id=uuid.uuid4(),
                account_id=account.id,
                type="deposit",
                amount=1000 * (i + 1),
                description=f"Transaction {i + 1}",
                created_at=str(datetime.now(UTC)),
            )
            in_memory_db.add(transaction)
        in_memory_db.commit()

        # Query transactions
        transactions = in_memory_db.query(Transaction).filter_by(account_id=account.id).all()
        assert len(transactions) == 5

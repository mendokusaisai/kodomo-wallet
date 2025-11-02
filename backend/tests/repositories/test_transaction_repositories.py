from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.repositories.sqlalchemy import SQLAlchemyTransactionRepository
from app.repositories.sqlalchemy.models import Account, Profile


# ============================================================================
# SQLAlchemyTransactionRepository Tests
# ============================================================================
class TestSQLAlchemyTransactionRepository:
    """SQLAlchemyTransactionRepository のテストスイート"""

    def test_create_transaction(
        self, in_memory_db: Session, sample_profile: Profile, sample_account: Account
    ):
        """トランザクションの作成をテスト"""
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

    def test_get_by_account_id(
        self, in_memory_db: Session, sample_profile: Profile, sample_account: Account
    ):
        """アカウント ID でトランザクションを取得できることをテスト"""
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

    def test_get_by_account_id_with_limit(
        self, in_memory_db: Session, sample_profile: Profile, sample_account: Account
    ):
        """limit パラメータが正しく動作することをテスト"""
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

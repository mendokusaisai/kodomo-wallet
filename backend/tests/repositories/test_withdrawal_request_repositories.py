import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.repositories.sqlalchemy import SQLAlchemyWithdrawalRequestRepository
from app.repositories.sqlalchemy.models import Account, FamilyRelationship, Profile


# ============================================================================
# SQLAlchemyWithdrawalRequestRepository Tests
# ============================================================================
class TestSQLAlchemyWithdrawalRequestRepository:
    """SQLAlchemyWithdrawalRequestRepository のテストスイート"""

    def test_create_withdrawal_request(
        self, in_memory_db: Session, sample_profile: Profile, sample_account: Account
    ):
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

    def test_get_by_id(
        self, in_memory_db: Session, sample_profile: Profile, sample_account: Account
    ):
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

    def test_get_by_id_returns_none_when_not_found(self, in_memory_db: Session):
        """存在しない ID で None を返すことをテスト"""
        repo = SQLAlchemyWithdrawalRequestRepository(in_memory_db)
        result = repo.get_by_id(str(uuid.uuid4()))
        assert result is None

    def test_get_pending_by_parent(self, in_memory_db: Session):
        """親の子に対する保留中の出金リクエスト取得をテスト"""
        # 親、子、アカウントを作成
        parent = Profile(
            id=uuid.uuid4(),
            name="Parent",
            email=None,
            role="parent",
            auth_user_id=None,
            avatar_url=None,
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        child = Profile(
            id=uuid.uuid4(),
            name="Child",
            email=None,
            role="child",
            auth_user_id=None,
            avatar_url=None,
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )

        account = Account(
            id=uuid.uuid4(),
            user_id=child.id,
            balance=10000,
            currency="JPY",
            goal_name=None,
            goal_amount=None,
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        fr = FamilyRelationship(
            id=uuid.uuid4(),
            parent_id=parent.id,
            child_id=child.id,
            relationship_type="parent",
            created_at=str(datetime.now(UTC)),
        )
        in_memory_db.add_all([parent, child, account, fr])
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

    def test_update_status(
        self, in_memory_db: Session, sample_profile: Profile, sample_account: Account
    ):
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

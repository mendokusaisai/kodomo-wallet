import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.repositories.mock_repositories import MockRecurringDepositRepository
from app.repositories.sqlalchemy import SQLAlchemyRecurringDepositRepository
from app.repositories.sqlalchemy.models import Account, Profile


# ============================================================================
# MockRecurringDepositRepository Tests
# ============================================================================
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


# ============================================================================
# SQLAlchemyRecurringDepositRepository Tests
# ============================================================================
class TestSQLAlchemyRecurringDepositRepository:
    """SQLAlchemyRecurringDepositRepository のテスト"""

    def test_create_recurring_deposit(self, in_memory_db: Session):
        """定期入金設定を作成できることをテスト"""
        # プロフィールとアカウントを作成
        profile = Profile(
            id=uuid.uuid4(),
            name="Parent",
            email=None,
            role="parent",
            parent_id=None,
            auth_user_id=None,
            avatar_url=None,
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        account = Account(
            id=uuid.uuid4(),
            user_id=profile.id,
            balance=0,
            currency="JPY",
            goal_name=None,
            goal_amount=None,
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

    def test_get_by_account_id(self, in_memory_db: Session):
        """account_idで定期入金設定を取得できることをテスト"""
        # プロフィールとアカウントを作成
        profile = Profile(
            id=uuid.uuid4(),
            name="Parent",
            email=None,
            role="parent",
            parent_id=None,
            auth_user_id=None,
            avatar_url=None,
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        account = Account(
            id=uuid.uuid4(),
            user_id=profile.id,
            balance=0,
            currency="JPY",
            goal_name=None,
            goal_amount=None,
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

    def test_get_by_account_id_returns_none_when_not_found(self, in_memory_db: Session):
        """存在しないaccount_idの場合Noneを返すことをテスト"""
        repo = SQLAlchemyRecurringDepositRepository(in_memory_db)
        account_id = str(uuid.uuid4())

        result = repo.get_by_account_id(account_id)
        assert result is None

    def test_update_recurring_deposit(self, in_memory_db: Session):
        """定期入金設定を更新できることをテスト"""
        # プロフィールとアカウントを作成
        profile = Profile(
            id=uuid.uuid4(),
            name="Parent",
            email=None,
            role="parent",
            parent_id=None,
            auth_user_id=None,
            avatar_url=None,
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        account = Account(
            id=uuid.uuid4(),
            user_id=profile.id,
            balance=0,
            currency="JPY",
            goal_name=None,
            goal_amount=None,
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
        assert not updated_rd.is_active

    def test_delete_recurring_deposit(self, in_memory_db: Session):
        """定期入金設定を削除できることをテスト"""
        # プロフィールとアカウントを作成
        profile = Profile(
            id=uuid.uuid4(),
            name="Parent",
            email=None,
            role="parent",
            parent_id=None,
            auth_user_id=None,
            avatar_url=None,
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        account = Account(
            id=uuid.uuid4(),
            user_id=profile.id,
            balance=0,
            currency="JPY",
            goal_name=None,
            goal_amount=None,
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

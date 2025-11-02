import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.domain.entities import Account as DomainAccount
from app.repositories.sqlalchemy import SQLAlchemyAccountRepository
from app.repositories.sqlalchemy.models import Account, Profile


# ============================================================================
# SQLAlchemyAccountRepository Tests
# ============================================================================
class TestSQLAlchemyAccountRepository:
    """SQLAlchemyAccountRepository のテストスイート"""

    def test_get_by_id_returns_none_when_not_found(self, in_memory_db: Session):
        """アカウントが存在しない場合に get_by_id が None を返すことをテスト"""
        repo = SQLAlchemyAccountRepository(in_memory_db)
        result = repo.get_by_id(str(uuid.uuid4()))
        assert result is None

    def test_add_and_get_account(
        self, in_memory_db: Session, sample_profile: Profile, sample_account: Account
    ):
        """アカウントを追加して取得できることをテスト"""
        in_memory_db.add(sample_profile)
        in_memory_db.add(sample_account)
        in_memory_db.commit()

        repo = SQLAlchemyAccountRepository(in_memory_db)
        result = repo.get_by_id(str(sample_account.id))

        assert result is not None
        assert result.id == str(sample_account.id)
        assert int(result.balance) == 10000

    def test_get_by_user_id(self, in_memory_db: Session, sample_profile: Profile):
        """ユーザーの全アカウントを取得できることをテスト"""
        account1 = Account(
            id=uuid.uuid4(),
            user_id=sample_profile.id,
            balance=5000,
            currency="JPY",
            goal_name=None,
            goal_amount=None,
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        account2 = Account(
            id=uuid.uuid4(),
            user_id=sample_profile.id,
            balance=3000,
            currency="JPY",
            goal_name=None,
            goal_amount=None,
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )

        in_memory_db.add(sample_profile)
        in_memory_db.add(account1)
        in_memory_db.add(account2)
        in_memory_db.commit()

        repo = SQLAlchemyAccountRepository(in_memory_db)
        results = repo.get_by_user_id(str(sample_profile.id))

        assert len(results) == 2
        assert all(str(acc.user_id) == str(sample_profile.id) for acc in results)

    def test_update_balance(
        self, in_memory_db: Session, sample_profile: Profile, sample_account: Account
    ):
        """アカウント残高の更新をテスト"""
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
        assert int(result.balance) == 15000

    def test_create_account(self, in_memory_db: Session, sample_profile: Profile):
        """新規アカウントを作成できることをテスト"""
        in_memory_db.add(sample_profile)
        in_memory_db.commit()

        repo = SQLAlchemyAccountRepository(in_memory_db)
        account = repo.create(user_id=str(sample_profile.id), balance=5000, currency="JPY")
        in_memory_db.commit()

        assert account.id is not None
        assert str(account.user_id) == str(sample_profile.id)
        assert int(account.balance) == 5000
        assert str(account.currency) == "JPY"
        assert account.goal_name is None
        assert account.goal_amount is None

        # DBから再取得して確認
        result = repo.get_by_id(str(account.id))
        assert result is not None
        assert str(result.user_id) == str(sample_profile.id)

    def test_create_account_with_initial_balance_zero(
        self, in_memory_db: Session, sample_profile: Profile
    ):
        """残高0でアカウントを作成できることをテスト"""
        in_memory_db.add(sample_profile)
        in_memory_db.commit()

        repo = SQLAlchemyAccountRepository(in_memory_db)
        account = repo.create(user_id=str(sample_profile.id), balance=0, currency="JPY")
        in_memory_db.commit()

        assert account.id is not None
        assert int(account.balance) == 0

    def test_update_account(
        self, in_memory_db: Session, sample_profile: Profile, sample_account: Account
    ):
        """アカウント全体を更新できることをテスト（goal設定など）"""
        in_memory_db.add(sample_profile)
        in_memory_db.add(sample_account)
        in_memory_db.commit()

        repo = SQLAlchemyAccountRepository(in_memory_db)
        account = repo.get_by_id(str(sample_account.id))
        assert account is not None

        # Goal設定を含む更新
        from app.domain.entities import Account as DomainAccount

        updated_account = DomainAccount(
            id=account.id,
            user_id=account.user_id,
            balance=account.balance,
            currency=account.currency,
            goal_name="新しいゲーム機",
            goal_amount=30000,
            created_at=account.created_at,
            updated_at=account.updated_at,
        )

        result = repo.update(updated_account)
        in_memory_db.commit()

        assert str(result.goal_name) == "新しいゲーム機"
        assert result.goal_amount == 30000

        # DBから再取得して確認
        fetched = repo.get_by_id(str(account.id))
        assert fetched is not None
        assert str(fetched.goal_name) == "新しいゲーム機"
        assert fetched.goal_amount == 30000

    def test_update_account_clear_goal(self, in_memory_db: Session, sample_profile: Profile):
        """アカウントのgoalをクリアできることをテスト"""
        # Goal設定済みのアカウントを作成
        account_with_goal = Account(
            id=uuid.uuid4(),
            user_id=sample_profile.id,
            balance=10000,
            currency="JPY",
            goal_name="Old Goal",
            goal_amount=20000,
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add(sample_profile)
        in_memory_db.add(account_with_goal)
        in_memory_db.commit()

        repo = SQLAlchemyAccountRepository(in_memory_db)

        # DBから取得してドメインエンティティを作成
        fetched_account = repo.get_by_id(str(account_with_goal.id))
        assert fetched_account is not None

        # Goalをクリア

        updated_account = DomainAccount(
            id=fetched_account.id,
            user_id=fetched_account.user_id,
            balance=fetched_account.balance,
            currency=fetched_account.currency,
            goal_name=None,
            goal_amount=None,
            created_at=fetched_account.created_at,
            updated_at=datetime.now(UTC),
        )

        result = repo.update(updated_account)
        in_memory_db.commit()

        assert result.goal_name is None
        assert result.goal_amount is None

        # DBから再取得して確認
        fetched = repo.get_by_id(str(account_with_goal.id))
        assert fetched is not None
        assert fetched.goal_name is None
        assert fetched.goal_amount is None

    def test_delete_account(
        self, in_memory_db: Session, sample_profile: Profile, sample_account: Account
    ):
        """アカウントを削除できることをテスト"""
        in_memory_db.add(sample_profile)
        in_memory_db.add(sample_account)
        in_memory_db.commit()

        repo = SQLAlchemyAccountRepository(in_memory_db)
        result = repo.delete(str(sample_account.id))
        in_memory_db.commit()

        assert result is True

        # 削除後は取得できない
        assert repo.get_by_id(str(sample_account.id)) is None

    def test_delete_returns_false_when_not_found(self, in_memory_db: Session):
        """存在しないアカウントの削除でFalseを返すことをテスト"""
        repo = SQLAlchemyAccountRepository(in_memory_db)
        result = repo.delete(str(uuid.uuid4()))
        assert result is False

    def test_get_by_user_id_returns_empty_when_no_accounts(
        self, in_memory_db: Session, sample_profile: Profile
    ):
        """アカウントがない場合に空のリストを返すことをテスト"""
        in_memory_db.add(sample_profile)
        in_memory_db.commit()

        repo = SQLAlchemyAccountRepository(in_memory_db)
        results = repo.get_by_user_id(str(sample_profile.id))

        assert len(results) == 0
        assert results == []

    def test_account_with_goal(self, in_memory_db: Session, sample_profile: Profile):
        """目標設定付きのアカウントを作成・取得できることをテスト"""
        account_with_goal = Account(
            id=uuid.uuid4(),
            user_id=sample_profile.id,
            balance=5000,
            currency="JPY",
            goal_name="自転車",
            goal_amount=25000,
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add(sample_profile)
        in_memory_db.add(account_with_goal)
        in_memory_db.commit()

        repo = SQLAlchemyAccountRepository(in_memory_db)
        result = repo.get_by_id(str(account_with_goal.id))

        assert result is not None
        assert str(result.goal_name) == "自転車"
        assert result.goal_amount == 25000
        assert int(result.balance) == 5000

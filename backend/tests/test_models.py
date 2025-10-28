"""SQLAlchemy モデルのユニットテスト

データベース制約、リレーションシップ、モデルの動作をテスト
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.repositories.sqlalchemy.models import Account, Profile, RecurringDeposit, Transaction


class TestProfileModel:
    """Profile モデルのテストスイート"""

    def test_create_parent_profile(self, in_memory_db: Session):
        """
        親プロフィールを作成できることを確認する
        期待値: 作成されたプロフィールが正しく保存されていること
        """
        profile = Profile(
            id=uuid.uuid4(),
            name="Parent User",
            email="parent@example.com",
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
        assert result.email == "parent@example.com"
        assert result.parent_id is None

    def test_create_child_profile_with_parent(self, in_memory_db: Session):
        """
        親との関係を持つ子プロフィールの作成を確認する
        期待値: 作成されたプロフィールが正しく親IDを参照していること
        """
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

    def test_profile_with_avatar_url(self, in_memory_db: Session):
        """
        オプションのアバター URL を持つプロフィールを作成できることを確認する
        期待値: 作成されたプロフィールが設定したアバター URL を持っていること
        """
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
    """Account モデルのテストスイート"""

    def test_create_account(self, in_memory_db: Session):
        """
        アカウントが作成できることを確認する
        期待値: 作成されたアカウントが保存されていること
        """
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

    def test_account_with_savings_goal(self, in_memory_db: Session):
        """
        貯金目標を持つアカウントを作成できることを確認する
        期待値: 作成されたアカウントが設定した貯金目標を持っていること
        """
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

    def test_multiple_accounts_per_user(self, in_memory_db: Session):
        """
        複数アカウントを持つユーザーを作成できることを確認する
        期待値: ユーザーが2つのアカウントを持っていること
        """
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
    """Transaction モデルのテストスイート"""

    def test_create_deposit_transaction(self, in_memory_db: Session):
        """
        入金トランザクショが作成できることを確認する
        期待値: 作成されたトランザクションが保存されていること
        """
        # 事前準備: プロフィールとアカウントを作成
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

        # トランザクションを作成
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
        assert str(result.account_id) == str(account.id)
        assert result.type == "deposit"
        assert result.amount == 5000
        assert result.description == "Test deposit"

    def test_transaction_types(self, in_memory_db: Session):
        """
        複数のトランザクション種別を作成できることを確認する
        期待値: 作成された各種別のトランザクションが保存されていること
        """
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

        transaction_types = ["deposit", "withdraw"]
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
        assert len(results) == 2
        types = {tx.type for tx in results}
        assert types == {"deposit", "withdraw"}

    def test_transaction_without_description(self, in_memory_db: Session):
        """
        説明なしのトランザクション作成が可能であることを確認する
        期待値: 説明が None のトランザクションが保存されていること
        """
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


class TestWithdrawalRequestModel:
    """WithdrawalRequest モデルのテストスイート"""

    def test_create_withdrawal_request(self, in_memory_db: Session):
        """出金リクエスト作成をテスト"""
        # 親/子とアカウントを作成
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

        from app.repositories.sqlalchemy.models import WithdrawalRequest

        req = WithdrawalRequest(
            id=uuid.uuid4(),
            account_id=account.id,
            amount=3000,
            description="Test withdraw",
            status="pending",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add(req)
        in_memory_db.commit()

        result = in_memory_db.query(WithdrawalRequest).filter_by(id=req.id).first()
        assert result is not None
        assert str(result.account_id) == str(account.id)
        assert int(result.amount) == 3000  # type: ignore[arg-type]
        assert str(result.status) == "pending"

    def test_withdrawal_request_default_status(self, in_memory_db: Session):
        """デフォルトのステータスをテスト"""
        # 子とアカウント
        child = Profile(
            id=uuid.uuid4(),
            name="Child",
            role="child",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        account = Account(
            id=uuid.uuid4(),
            user_id=child.id,
            balance=5000,
            currency="JPY",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add_all([child, account])
        in_memory_db.commit()

        from app.repositories.sqlalchemy.models import WithdrawalRequest

        r1 = WithdrawalRequest(
            id=uuid.uuid4(),
            account_id=account.id,
            amount=1000,
            description=None,
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        r2 = WithdrawalRequest(
            id=uuid.uuid4(),
            account_id=account.id,
            amount=1500,
            description="Snack",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add_all([r1, r2])
        in_memory_db.commit()

        # ステータスはデフォルトで pending
        assert str(r1.status) == "pending"
        assert str(r2.status) == "pending"


class TestRecurringDepositModel:
    """RecurringDeposit モデルのテストスイート"""

    def test_create_recurring_deposit(self, in_memory_db: Session):
        """
        定期入金設定を作成できることを確認する
        期待値: 作成された定期入金設定が正しく保存されていること
        """
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
        recurring_deposit = RecurringDeposit(
            id=uuid.uuid4(),
            account_id=account.id,
            amount=5000,
            day_of_month=15,
            is_active="true",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add(recurring_deposit)
        in_memory_db.commit()

        # データベースから取得して確認
        result = in_memory_db.query(RecurringDeposit).filter_by(id=recurring_deposit.id).first()
        assert result is not None
        assert result.account_id == account.id
        assert result.amount == 5000
        assert result.day_of_month == 15
        assert result.is_active == "true"

    def test_recurring_deposit_default_is_active(self, in_memory_db: Session):
        """
        定期入金設定のデフォルト値（is_active=true）をテスト
        期待値: is_activeが未指定の場合、デフォルトで"true"になること
        """
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

        # is_activeを指定せずに定期入金設定を作成
        recurring_deposit = RecurringDeposit(
            id=uuid.uuid4(),
            account_id=account.id,
            amount=3000,
            day_of_month=1,
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add(recurring_deposit)
        in_memory_db.commit()

        # データベースから取得して確認
        result = in_memory_db.query(RecurringDeposit).filter_by(id=recurring_deposit.id).first()
        assert result is not None
        assert result.is_active == "true"

    def test_recurring_deposit_amount_constraint(self, in_memory_db: Session):
        """
        定期入金設定の金額制約（amount > 0）をテスト
        期待値: 負の金額でエラーが発生すること
        """
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

        # 負の金額で定期入金設定を作成しようとする
        recurring_deposit = RecurringDeposit(
            id=uuid.uuid4(),
            account_id=account.id,
            amount=0,  # 不正な金額
            day_of_month=10,
            is_active="true",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add(recurring_deposit)

        # コミット時にエラーが発生することを確認
        import pytest
        from sqlalchemy.exc import IntegrityError

        with pytest.raises(IntegrityError):
            in_memory_db.commit()

    def test_recurring_deposit_day_of_month_constraint(self, in_memory_db: Session):
        """
        定期入金設定の日付制約（1 <= day_of_month <= 31）をテスト
        期待値: 範囲外の日付でエラーが発生すること
        """
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

        # 範囲外の日付で定期入金設定を作成しようとする
        recurring_deposit = RecurringDeposit(
            id=uuid.uuid4(),
            account_id=account.id,
            amount=5000,
            day_of_month=32,  # 不正な日付
            is_active="true",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add(recurring_deposit)

        # コミット時にエラーが発生することを確認
        import pytest
        from sqlalchemy.exc import IntegrityError

        with pytest.raises(IntegrityError):
            in_memory_db.commit()


class TestModelRelationships:
    """モデル間のリレーションシップのテスト"""

    def test_profile_to_accounts_relationship(self, in_memory_db: Session):
        """プロフィールから自身のアカウントにアクセスできることをテスト"""
        profile = Profile(
            id=uuid.uuid4(),
            name="User",
            role="parent",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add(profile)
        in_memory_db.commit()

        # 複数のアカウントを作成
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

        # user_id を用いてアカウントを取得
        accounts = in_memory_db.query(Account).filter_by(user_id=profile.id).all()
        assert len(accounts) == 3

    def test_account_to_transactions_relationship(self, in_memory_db: Session):
        """アカウントから自身のトランザクションにアクセスできることをテスト"""
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

        # 複数のトランザクションを作成
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

        # トランザクションを取得
        transactions = in_memory_db.query(Transaction).filter_by(account_id=account.id).all()
        assert len(transactions) == 5

    def test_account_to_withdrawal_requests_relationship(self, in_memory_db: Session):
        """アカウントから出金リクエストにアクセスできることをテスト"""
        child = Profile(
            id=uuid.uuid4(),
            name="Child",
            role="child",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        account = Account(
            id=uuid.uuid4(),
            user_id=child.id,
            balance=5000,
            currency="JPY",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add_all([child, account])
        in_memory_db.commit()

        from app.repositories.sqlalchemy.models import WithdrawalRequest

        # 複数の出金リクエストを作成
        r1 = WithdrawalRequest(
            id=uuid.uuid4(),
            account_id=account.id,
            amount=1000,
            description=None,
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        r2 = WithdrawalRequest(
            id=uuid.uuid4(),
            account_id=account.id,
            amount=1500,
            description="Snack",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add_all([r1, r2])
        in_memory_db.commit()

        # リレーションを確認
        refreshed_account = in_memory_db.query(Account).filter_by(id=account.id).first()
        assert refreshed_account is not None
        assert len(refreshed_account.withdrawal_requests) == 2  # type: ignore[index]

    def test_account_to_recurring_deposit_relationship(self, in_memory_db: Session):
        """アカウントから定期入金設定にアクセスできることをテスト"""
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
        recurring_deposit = RecurringDeposit(
            id=uuid.uuid4(),
            account_id=account.id,
            amount=10000,
            day_of_month=25,
            is_active="true",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add(recurring_deposit)
        in_memory_db.commit()

        # リレーションを確認
        refreshed_account = in_memory_db.query(Account).filter_by(id=account.id).first()
        assert refreshed_account is not None
        assert len(refreshed_account.recurring_deposits) == 1  # type: ignore[index]
        assert refreshed_account.recurring_deposits[0].amount == 10000  # type: ignore[index]

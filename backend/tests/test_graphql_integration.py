"""GraphQL Resolver の統合テスト

データベース統合を含むリゾルバー関数のテスト
"""

import uuid
from datetime import UTC, datetime

import pytest
from sqlalchemy.orm import Session

from app.api.graphql import resolvers
from app.repositories.sqlalchemy import (
    SQLAlchemyAccountRepository,
    SQLAlchemyProfileRepository,
    SQLAlchemyTransactionRepository,
)
from app.repositories.sqlalchemy.models import Account, Profile, Transaction
from app.services import (
    AccountService,
    ProfileService,
    TransactionService,
)


@pytest.fixture
def services(in_memory_db: Session):
    """リポジトリを含むサービスインスタンスを作成"""
    profile_repo = SQLAlchemyProfileRepository(in_memory_db)
    account_repo = SQLAlchemyAccountRepository(in_memory_db)
    transaction_repo = SQLAlchemyTransactionRepository(in_memory_db)

    profile_service = ProfileService(profile_repo, account_repo)
    account_service = AccountService(account_repo, profile_repo)
    transaction_service = TransactionService(transaction_repo, account_repo)

    return {
        "profile": profile_service,
        "account": account_service,
        "transaction": transaction_service,
    }


@pytest.fixture
def profile_service(services) -> ProfileService:
    """プロフィールサービスのフィクスチャ"""
    return services["profile"]


@pytest.fixture
def account_service(services) -> AccountService:
    """アカウントサービスのフィクスチャ"""
    return services["account"]


@pytest.fixture
def transaction_service(services) -> TransactionService:
    """トランザクションサービスのフィクスチャ"""
    return services["transaction"]


@pytest.fixture
def parent_profile(in_memory_db: Session) -> Profile:
    """親プロフィール"""
    parent_profile = Profile(
        id=uuid.uuid4(),
        name="Parent User",
        role="parent",
        created_at=str(datetime.now(UTC)),
        updated_at=str(datetime.now(UTC)),
    )
    in_memory_db.add(parent_profile)
    in_memory_db.commit()
    return parent_profile


@pytest.fixture
def child_profile(in_memory_db: Session, parent_profile: Profile) -> Profile:
    """子プロフィール"""
    child_profile = Profile(
        id=uuid.uuid4(),
        name="Child User",
        role="child",
        parent_id=parent_profile.id,
        created_at=str(datetime.now(UTC)),
        updated_at=str(datetime.now(UTC)),
    )
    in_memory_db.add(child_profile)
    in_memory_db.commit()
    return child_profile


@pytest.fixture
def child_account(in_memory_db: Session, child_profile: Profile) -> Account:
    """子アカウント"""
    account = Account(
        id=uuid.uuid4(),
        user_id=child_profile.id,
        balance=10000,
        currency="JPY",
        goal_name="Test Goal",
        goal_amount=50000,
        created_at=str(datetime.now(UTC)),
        updated_at=str(datetime.now(UTC)),
    )
    in_memory_db.add(account)
    in_memory_db.commit()
    return account


@pytest.fixture
def transaction(in_memory_db: Session, child_account: Account) -> Transaction:
    """子アカウントのトランザクション"""
    transaction = Transaction(
        id=uuid.uuid4(),
        account_id=child_account.id,
        type="deposit",
        amount=5000,
        description="Initial deposit",
        created_at=str(datetime.now(UTC)),
    )
    in_memory_db.add(transaction)
    in_memory_db.commit()
    return transaction


class TestResolverIntegration:
    """データベース統合を含むリゾルバー関数のテスト"""

    def test_get_profile_by_id(self, parent_profile: Profile, profile_service: ProfileService):
        """ID によるプロフィール取得のテスト"""
        profile_id = str(parent_profile.id)
        result = resolvers.get_profile_by_id(profile_id, profile_service)

        assert result is not None
        assert result.id == str(parent_profile.id)
        assert result.name == "Parent User"
        assert result.role == "parent"

    def test_get_profile_not_found(self, profile_service: ProfileService):
        """存在しないプロフィールの取得で None が返ることをテスト"""
        result = resolvers.get_profile_by_id(str(uuid.uuid4()), profile_service)
        assert result is None

    def test_get_accounts_by_user_id(
        self,
        parent_profile: Profile,
        child_account: Account,
        profile_service: ProfileService,
        account_service: AccountService,
    ):
        """ユーザーのアカウント取得のテスト"""
        # 親ユーザーIDを使用（親は子供のアカウントを取得）
        user_id = str(parent_profile.id)
        results = resolvers.get_accounts_by_user_id(user_id, account_service, profile_service)

        assert len(results) == 1
        assert results[0].id == str(child_account.id)
        assert results[0].balance == 10000
        assert results[0].currency == "JPY"

    def test_get_accounts_empty(
        self, account_service: AccountService, profile_service: ProfileService
    ):
        """存在しないユーザーのアカウント取得のテスト"""
        results = resolvers.get_accounts_by_user_id(
            str(uuid.uuid4()), account_service, profile_service
        )
        assert results == []

    def test_get_transactions_by_account_id(
        self,
        child_account: Account,
        transaction: Transaction,
        transaction_service: TransactionService,
    ):
        """アカウントのトランザクション取得のテスト"""
        account_id = str(child_account.id)
        results = resolvers.get_transactions_by_account_id(
            account_id, transaction_service, limit=10
        )

        assert len(results) == 1
        assert results[0].type == "deposit"
        assert results[0].amount == 5000
        assert results[0].description == "Initial deposit"

    def test_get_transactions_empty(self, transaction_service: TransactionService):
        """存在しないアカウントのトランザクション取得のテスト"""
        results = resolvers.get_transactions_by_account_id(
            str(uuid.uuid4()), transaction_service, limit=10
        )
        assert results == []

    def test_create_deposit(
        self, in_memory_db: Session, child_account: Account, transaction_service: TransactionService
    ):
        """入金作成のテスト"""
        account_id = str(child_account.id)
        initial_balance = child_account.balance

        transaction = resolvers.create_deposit(
            account_id, 3000, transaction_service, "Test deposit"
        )

        assert transaction is not None
        assert transaction.type == "deposit"
        assert transaction.amount == 3000
        assert transaction.description == "Test deposit"

        # 残高が更新されたことを確認（実際の使用では context manager でコミット）
        in_memory_db.commit()
        in_memory_db.refresh(child_account)
        assert child_account.balance == initial_balance + 3000

    def test_create_deposit_account_not_found(self, transaction_service: TransactionService):
        """存在しないアカウントへの入金作成のテスト"""
        with pytest.raises(Exception, match="Account .* not found"):
            resolvers.create_deposit(str(uuid.uuid4()), 1000, transaction_service, "Test")

    def test_create_deposit_updates_transaction_list(
        self,
        in_memory_db: Session,
        child_account: Account,
        transaction: Transaction,
        transaction_service: TransactionService,
    ):
        """入金がクエリ可能なトランザクションを作成することをテスト"""
        account_id = str(child_account.id)

        # 入金を作成
        resolvers.create_deposit(account_id, 2000, transaction_service, "New deposit")

        # トランザクションを可視化するためにコミット（実際の使用では context manager で実施）
        in_memory_db.commit()

        # トランザクションをクエリ
        transactions = resolvers.get_transactions_by_account_id(account_id, transaction_service)

        # 初期 + 新規で 2 件のトランザクションがあるはず
        assert len(transactions) == 2

    def test_multiple_deposits(
        self,
        in_memory_db: Session,
        child_account: Account,
        transaction: Transaction,
        transaction_service: TransactionService,
    ):
        """複数回の入金作成のテスト"""
        account_id = str(child_account.id)
        initial_balance = child_account.balance

        resolvers.create_deposit(account_id, 1000, transaction_service, "Deposit 1")
        resolvers.create_deposit(account_id, 2000, transaction_service, "Deposit 2")
        resolvers.create_deposit(account_id, 3000, transaction_service, "Deposit 3")

        # Commit to update balance (in real usage, done by context manager)
        in_memory_db.commit()

        # Verify final balance
        in_memory_db.refresh(child_account)
        assert child_account.balance == initial_balance + 6000

        # Verify transaction count
        transactions = resolvers.get_transactions_by_account_id(account_id, transaction_service)
        assert len(transactions) == 4  # 1 initial + 3 new

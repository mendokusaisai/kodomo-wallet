"""TransactionService のユニットテスト"""

from dataclasses import replace
from datetime import UTC, datetime

import pytest
from injector import Injector

from app.core.exceptions import InvalidAmountException, ResourceNotFoundException
from app.domain.entities import Account
from app.repositories.mock_repositories import (
    MockAccountRepository,
    MockProfileRepository,
    MockTransactionRepository,
)
from app.services import TransactionService

from .conftest import RepositoryModule


class TestTransactionService:
    """TransactionService のテストスイート"""

    def test_get_account_transactions_success(
        self,
        injector_with_mocks: Injector,
        mock_account_repository: MockAccountRepository,
        mock_transaction_repository: MockTransactionRepository,
        sample_account: Account,
    ):
        """アカウントトランザクションの取得成功をテスト"""
        # 準備: アカウントとトランザクションを追加
        mock_account_repository.add(sample_account)
        mock_transaction_repository.create(
            account_id=sample_account.id,
            transaction_type="deposit",
            amount=1000,
            description="Test 1",
            created_at=datetime.now(UTC),
        )
        mock_transaction_repository.create(
            account_id=sample_account.id,
            transaction_type="withdraw",
            amount=500,
            description="Test 2",
            created_at=datetime.now(UTC),
        )

        # テスト: サービスを取得してトランザクションを取得
        service = injector_with_mocks.get(TransactionService)
        results = service.get_account_transactions(str(sample_account.id))

        # 検証
        assert len(results) == 2

    def test_get_account_transactions_with_limit(
        self,
        injector_with_mocks: Injector,
        mock_account_repository: MockAccountRepository,
        mock_transaction_repository: MockTransactionRepository,
        sample_account: Account,
    ):
        """リミット付きトランザクション取得をテスト"""
        # 準備: アカウントと複数のトランザクションを追加
        mock_account_repository.add(sample_account)
        for i in range(5):
            mock_transaction_repository.create(
                account_id=sample_account.id,
                transaction_type="deposit",
                amount=1000 * (i + 1),
                description=f"Transaction {i + 1}",
                created_at=datetime.now(UTC),
            )

        # テスト: サービスを取得してリミット付きでトランザクションを取得
        service = injector_with_mocks.get(TransactionService)
        results = service.get_account_transactions(str(sample_account.id), limit=3)

        # 検証
        assert len(results) == 3

    def test_create_deposit_success(
        self,
        injector_with_mocks: Injector,
        mock_account_repository: MockAccountRepository,
        mock_transaction_repository: MockTransactionRepository,
        sample_account: Account,
    ):
        """入金作成の成功をテスト"""
        # 準備: リポジトリにアカウントを追加
        mock_account_repository.add(sample_account)
        initial_balance = sample_account.balance

        # テスト: 入金を作成
        service = injector_with_mocks.get(TransactionService)
        transaction = service.create_deposit(
            account_id=str(sample_account.id),
            amount=500,
            description="Test deposit",
        )

        # 検証: トランザクション
        assert transaction is not None
        assert str(transaction.account_id) == str(sample_account.id)
        assert str(transaction.type) == "deposit"
        assert int(transaction.amount) == 500
        assert str(transaction.description) == "Test deposit"

        # 検証: 残高が更新されたことを確認
        updated_account = mock_account_repository.get_by_id(str(sample_account.id))
        assert updated_account is not None
        assert int(updated_account.balance) == initial_balance + 500

        # 検証: トランザクションが記録されたことを確認
        transactions = mock_transaction_repository.get_by_account_id(str(sample_account.id))
        assert len(transactions) == 1
        assert int(transactions[0].amount) == 500

    def test_create_deposit_account_not_found(self, injector_with_mocks: Injector):
        """存在しないアカウントへの入金でエラーが発生することをテスト"""
        service = injector_with_mocks.get(TransactionService)

        with pytest.raises(ResourceNotFoundException) as exc_info:
            service.create_deposit(
                account_id="non-existent-id",
                amount=500,
                description="Test deposit",
            )

        # 検証: 例外の詳細
        assert exc_info.value.resource_type == "Account"
        assert exc_info.value.resource_id == "non-existent-id"
        assert "not found" in str(exc_info.value)

    def test_create_deposit_updates_balance_correctly(
        self,
        injector_with_mocks: Injector,
        mock_account_repository: MockAccountRepository,
        sample_account: Account,
    ):
        """複数回の入金が残高を正しく更新することをテスト"""
        # 準備
        mock_account_repository.add(sample_account)
        initial_balance = int(sample_account.balance)

        # テスト: 複数回の入金を作成
        service = injector_with_mocks.get(TransactionService)
        service.create_deposit(sample_account.id, 100, "Deposit 1")
        service.create_deposit(sample_account.id, 200, "Deposit 2")
        service.create_deposit(sample_account.id, 300, "Deposit 3")

        # 検証: 最終残高が正しいことを確認
        updated_account = mock_account_repository.get_by_id(sample_account.id)
        assert updated_account is not None
        expected_balance = initial_balance + 100 + 200 + 300
        assert int(updated_account.balance) == expected_balance

    def test_create_deposit_without_description(
        self,
        injector_with_mocks: Injector,
        mock_account_repository: MockAccountRepository,
        sample_account: Account,
    ):
        """説明なしの入金作成をテスト"""
        # 準備
        mock_account_repository.add(sample_account)

        # テスト: 説明なしで入金を作成
        service = injector_with_mocks.get(TransactionService)
        transaction = service.create_deposit(
            account_id=str(sample_account.id),
            amount=500,
        )

        # 検証
        assert transaction is not None
        assert transaction.description is None

    def test_create_deposit_with_negative_amount(
        self,
        injector_with_mocks: Injector,
        mock_account_repository: MockAccountRepository,
        sample_account: Account,
    ):
        """負の金額での入金作成でエラーが発生することをテスト"""
        # 準備
        mock_account_repository.add(sample_account)

        # テスト
        service = injector_with_mocks.get(TransactionService)
        with pytest.raises(InvalidAmountException) as exc_info:
            service.create_deposit(
                account_id=sample_account.id,
                amount=-100,
                description="Invalid deposit",
            )

        # 検証: 例外の詳細
        assert exc_info.value.amount == -100
        assert "greater than zero" in exc_info.value.reason

    def test_create_deposit_with_zero_amount(
        self,
        injector_with_mocks: Injector,
        mock_account_repository: MockAccountRepository,
        sample_account: Account,
    ):
        """ゼロ金額での入金作成でエラーが発生することをテスト"""
        # 準備
        mock_account_repository.add(sample_account)

        # テスト
        service = injector_with_mocks.get(TransactionService)
        with pytest.raises(InvalidAmountException) as exc_info:
            service.create_deposit(
                account_id=sample_account.id,
                amount=0,
                description="Zero deposit",
            )

        # 検証: 例外の詳細
        assert exc_info.value.amount == 0
        assert "greater than zero" in exc_info.value.reason

    def test_service_uses_correct_repositories(
        self,
        mock_account_repository: MockAccountRepository,
        mock_transaction_repository: MockTransactionRepository,
        sample_account: Account,
    ):
        """TransactionServiceが両方の注入されたリポジトリを使用することをテスト"""
        # 準備
        mock_account_repository.add(sample_account)

        # 特定のリポジトリを持つインジェクターを作成
        injector = Injector(
            [
                RepositoryModule(
                    MockProfileRepository(),
                    mock_account_repository,
                    mock_transaction_repository,
                ),
            ]
        )

        # テスト
        service = injector.get(TransactionService)
        service.create_deposit(sample_account.id, 500, "Test")

        # 検証: 両方のリポジトリが使用されたことを確認
        assert mock_account_repository.get_by_id(sample_account.id) is not None
        assert len(mock_transaction_repository.get_by_account_id(sample_account.id)) == 1

    def test_create_withdraw_success(
        self,
        injector_with_mocks: Injector,
        mock_account_repository: MockAccountRepository,
        sample_account: Account,
    ):
        """出金作成の成功をテスト"""
        # 準備: 十分な残高を持つアカウントを追加
        account_with_balance = replace(sample_account, balance=10000)
        mock_account_repository.add(account_with_balance)
        initial_balance = int(account_with_balance.balance)

        # テスト: 出金を作成
        service = injector_with_mocks.get(TransactionService)
        transaction = service.create_withdraw(
            account_id=str(account_with_balance.id),
            amount=3000,
            description="Test withdrawal",
        )

        # 検証: トランザクション
        assert transaction is not None
        assert transaction.account_id == account_with_balance.id
        assert transaction.type == "withdraw"
        assert transaction.amount == 3000

        # 検証: 残高が減少したことを確認
        updated_account = mock_account_repository.get_by_id(account_with_balance.id)
        assert updated_account is not None
        assert updated_account.balance == initial_balance - 3000

    def test_create_withdraw_insufficient_balance(
        self,
        injector_with_mocks: Injector,
        mock_account_repository: MockAccountRepository,
        sample_account: Account,
    ):
        """残高不足での出金エラーをテスト"""
        # 準備: 少額の残高を持つアカウント
        account_low_balance = replace(sample_account, balance=1000)
        mock_account_repository.add(account_low_balance)

        # テスト: 残高を超える出金を試みる
        service = injector_with_mocks.get(TransactionService)

        with pytest.raises(InvalidAmountException) as exc_info:
            service.create_withdraw(
                account_id=account_low_balance.id,
                amount=5000,
                description="Too much withdrawal",
            )

        # 検証: 例外の詳細
        assert exc_info.value.amount == 5000
        assert "Insufficient balance" in exc_info.value.reason
        assert "Current: 1000" in exc_info.value.reason

    def test_create_withdraw_account_not_found(self, injector_with_mocks: Injector):
        """存在しないアカウントへの出金エラーをテスト"""
        # テスト: 存在しないアカウントに出金を試みる
        service = injector_with_mocks.get(TransactionService)

        with pytest.raises(ResourceNotFoundException) as exc_info:
            service.create_withdraw(
                account_id="non-existent-account",
                amount=1000,
                description="Test withdrawal",
            )

        # 検証
        assert exc_info.value.resource_type == "Account"
        assert exc_info.value.resource_id == "non-existent-account"

    def test_create_withdraw_with_negative_amount(
        self,
        injector_with_mocks: Injector,
        mock_account_repository: MockAccountRepository,
        sample_account: Account,
    ):
        """負の金額での出金エラーをテスト"""
        # 準備
        mock_account_repository.add(sample_account)

        # テスト: 負の金額で出金を試みる
        service = injector_with_mocks.get(TransactionService)

        with pytest.raises(InvalidAmountException) as exc_info:
            service.create_withdraw(
                account_id=str(sample_account.id),
                amount=-500,
                description="Negative withdrawal",
            )

        # 検証: 例外の詳細
        assert exc_info.value.amount == -500
        assert "greater than zero" in exc_info.value.reason

    def test_create_withdraw_with_zero_amount(
        self,
        injector_with_mocks: Injector,
        mock_account_repository: MockAccountRepository,
        sample_account: Account,
    ):
        """ゼロ金額での出金エラーをテスト"""
        # 準備
        mock_account_repository.add(sample_account)

        # テスト: ゼロ金額で出金を試みる
        service = injector_with_mocks.get(TransactionService)

        with pytest.raises(InvalidAmountException) as exc_info:
            service.create_withdraw(
                account_id=str(sample_account.id),
                amount=0,
                description="Zero withdrawal",
            )

        # 検証: 例外の詳細
        assert exc_info.value.amount == 0
        assert "greater than zero" in exc_info.value.reason

    def test_create_withdraw_exact_balance(
        self,
        injector_with_mocks: Injector,
        mock_account_repository: MockAccountRepository,
        sample_account: Account,
    ):
        """残高ちょうどの金額での出金成功をテスト"""
        # 準備: 特定の残高を持つアカウント
        account_with_balance = replace(sample_account, balance=5000)
        mock_account_repository.add(account_with_balance)

        # テスト: 残高ちょうどの出金
        service = injector_with_mocks.get(TransactionService)
        transaction = service.create_withdraw(
            account_id=str(account_with_balance.id),
            amount=5000,
            description="Full withdrawal",
        )

        # 検証: トランザクションが成功し、残高が0になる
        assert transaction is not None
        updated_account = mock_account_repository.get_by_id(str(account_with_balance.id))
        assert updated_account is not None
        assert int(updated_account.balance) == 0

    def test_create_withdraw_without_description(
        self,
        injector_with_mocks: Injector,
        mock_account_repository: MockAccountRepository,
        sample_account: Account,
    ):
        """説明なしでの出金作成をテスト"""
        # 準備
        account_with_balance = replace(sample_account, balance=10000)
        mock_account_repository.add(account_with_balance)

        # テスト: 説明なしで出金
        service = injector_with_mocks.get(TransactionService)
        transaction = service.create_withdraw(
            account_id=account_with_balance.id,
            amount=1000,
        )

        # 検証: トランザクションが作成される
        assert transaction is not None
        assert str(transaction.type) == "withdraw"

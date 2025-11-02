"""WithdrawalRequestService のユニットテスト"""

from datetime import UTC, datetime

import pytest
from injector import Injector

from app.core.exceptions import InvalidAmountException, ResourceNotFoundException
from app.domain.entities import Account
from app.repositories.mock_repositories import (
    MockAccountRepository,
    MockProfileRepository,
    MockTransactionRepository,
    MockWithdrawalRequestRepository,
)
from app.services import TransactionService, WithdrawalRequestService

from .conftest import RepositoryModule


class TestWithdrawalRequestService:
    """WithdrawalRequestService のテストスイート"""

    def test_create_withdrawal_request_success(
        self,
        mock_withdrawal_request_repository: MockWithdrawalRequestRepository,
        mock_account_repository: MockAccountRepository,
        sample_account: Account,
    ):
        """出金リクエスト作成の成功をテスト"""
        # 準備
        mock_account_repository.add(sample_account)

        injector = Injector(
            [
                RepositoryModule(
                    MockProfileRepository(),
                    mock_account_repository,
                    MockTransactionRepository(),
                    mock_withdrawal_request_repository,
                ),
            ]
        )

        service = injector.get(WithdrawalRequestService)

        # テスト
        result = service.create_withdrawal_request(str(sample_account.id), 3000, "Snacks")

        # 検証
        assert result is not None
        assert int(result.amount) == 3000  # type: ignore[arg-type]
        assert str(result.status) == "pending"
        assert str(result.description) == "Snacks"

    def test_create_withdrawal_request_with_invalid_amount(
        self,
        mock_withdrawal_request_repository: MockWithdrawalRequestRepository,
        mock_account_repository: MockAccountRepository,
        sample_account: Account,
    ):
        """金額が0以下の場合にエラーをテスト"""
        mock_account_repository.add(sample_account)

        injector = Injector(
            [
                RepositoryModule(
                    MockProfileRepository(),
                    mock_account_repository,
                    MockTransactionRepository(),
                    mock_withdrawal_request_repository,
                ),
            ]
        )

        service = injector.get(WithdrawalRequestService)

        # 0の場合
        with pytest.raises(InvalidAmountException) as exc_info:
            service.create_withdrawal_request(str(sample_account.id), 0, "Test")
        assert exc_info.value.amount == 0

        # 負の場合
        with pytest.raises(InvalidAmountException) as exc_info:
            service.create_withdrawal_request(str(sample_account.id), -500, "Test")
        assert exc_info.value.amount == -500

    def test_create_withdrawal_request_account_not_found(
        self,
        mock_withdrawal_request_repository: MockWithdrawalRequestRepository,
        mock_account_repository: MockAccountRepository,
    ):
        """存在しないアカウントの場合にエラーをテスト"""
        injector = Injector(
            [
                RepositoryModule(
                    MockProfileRepository(),
                    mock_account_repository,
                    MockTransactionRepository(),
                    mock_withdrawal_request_repository,
                ),
            ]
        )

        service = injector.get(WithdrawalRequestService)

        with pytest.raises(ResourceNotFoundException) as exc_info:
            service.create_withdrawal_request("non-existent-id", 1000, "Test")
        assert exc_info.value.resource_type == "Account"

    def test_create_withdrawal_request_insufficient_balance(
        self,
        mock_withdrawal_request_repository: MockWithdrawalRequestRepository,
        mock_account_repository: MockAccountRepository,
        sample_account: Account,
    ):
        """残高不足の場合にエラーをテスト"""
        # 残高10000のアカウント
        mock_account_repository.add(sample_account)

        injector = Injector(
            [
                RepositoryModule(
                    MockProfileRepository(),
                    mock_account_repository,
                    MockTransactionRepository(),
                    mock_withdrawal_request_repository,
                ),
            ]
        )

        service = injector.get(WithdrawalRequestService)

        # 残高を超える金額でリクエスト
        with pytest.raises(InvalidAmountException) as exc_info:
            service.create_withdrawal_request(str(sample_account.id), 15000, "Too much")
        assert "Insufficient balance" in exc_info.value.reason

    def test_get_pending_requests_for_parent(
        self,
        mock_withdrawal_request_repository: MockWithdrawalRequestRepository,
        mock_account_repository: MockAccountRepository,
        sample_account: Account,
    ):
        """親の子に対する保留中リクエスト取得をテスト"""
        mock_account_repository.add(sample_account)

        # 2件の出金リクエストを作成
        wr1 = mock_withdrawal_request_repository.create(
            account_id=str(sample_account.id),
            amount=1000,
            description="Request 1",
            created_at=datetime.now(UTC),
        )
        wr2 = mock_withdrawal_request_repository.create(
            account_id=str(sample_account.id),
            amount=1500,
            description="Request 2",
            created_at=datetime.now(UTC),
        )

        # 1件をapprovedに
        mock_withdrawal_request_repository.update_status(wr1, "approved", datetime.now(UTC))

        injector = Injector(
            [
                RepositoryModule(
                    MockProfileRepository(),
                    mock_account_repository,
                    MockTransactionRepository(),
                    mock_withdrawal_request_repository,
                ),
            ]
        )

        service = injector.get(WithdrawalRequestService)

        # テスト
        results = service.get_pending_requests_for_parent("parent-id")

        # 検証: pendingのみ
        assert len(results) == 1
        assert str(results[0].id) == str(wr2.id)

    def test_approve_withdrawal_request_success(
        self,
        mock_withdrawal_request_repository: MockWithdrawalRequestRepository,
        mock_account_repository: MockAccountRepository,
        mock_transaction_repository: MockTransactionRepository,
        sample_account: Account,
    ):
        """出金リクエスト承認の成功をテスト"""
        mock_account_repository.add(sample_account)

        # 出金リクエストを作成
        wr = mock_withdrawal_request_repository.create(
            account_id=str(sample_account.id),
            amount=3000,
            description="Approved request",
            created_at=datetime.now(UTC),
        )

        injector = Injector(
            [
                RepositoryModule(
                    MockProfileRepository(),
                    mock_account_repository,
                    mock_transaction_repository,
                    mock_withdrawal_request_repository,
                ),
            ]
        )

        service = injector.get(WithdrawalRequestService)
        transaction_service = injector.get(TransactionService)

        # テスト
        result = service.approve_withdrawal_request(str(wr.id), transaction_service)

        # 検証
        assert str(result.status) == "approved"

        # 残高が減っていることを確認
        updated_account = mock_account_repository.get_by_id(str(sample_account.id))
        assert updated_account is not None
        assert int(updated_account.balance) == 10000 - 3000  # type: ignore[arg-type]

        # トランザクションが作成されたことを確認
        transactions = mock_transaction_repository.get_by_account_id(str(sample_account.id))
        assert len(transactions) == 1
        assert str(transactions[0].type) == "withdraw"
        assert int(transactions[0].amount) == 3000  # type: ignore[arg-type]

    def test_approve_withdrawal_request_not_found(
        self,
        mock_withdrawal_request_repository: MockWithdrawalRequestRepository,
        mock_account_repository: MockAccountRepository,
    ):
        """存在しないリクエストの承認でエラーをテスト"""
        injector = Injector(
            [
                RepositoryModule(
                    MockProfileRepository(),
                    mock_account_repository,
                    MockTransactionRepository(),
                    mock_withdrawal_request_repository,
                ),
            ]
        )

        service = injector.get(WithdrawalRequestService)
        transaction_service = injector.get(TransactionService)

        with pytest.raises(ResourceNotFoundException) as exc_info:
            service.approve_withdrawal_request("non-existent-id", transaction_service)
        assert exc_info.value.resource_type == "WithdrawalRequest"

    def test_approve_withdrawal_request_already_processed(
        self,
        mock_withdrawal_request_repository: MockWithdrawalRequestRepository,
        mock_account_repository: MockAccountRepository,
        mock_transaction_repository: MockTransactionRepository,
        sample_account: Account,
    ):
        """既に処理済みのリクエスト承認でエラーをテスト"""
        mock_account_repository.add(sample_account)

        wr = mock_withdrawal_request_repository.create(
            account_id=str(sample_account.id),
            amount=2000,
            description="Already approved",
            created_at=datetime.now(UTC),
        )

        # 先に承認済みに
        mock_withdrawal_request_repository.update_status(wr, "approved", datetime.now(UTC))

        injector = Injector(
            [
                RepositoryModule(
                    MockProfileRepository(),
                    mock_account_repository,
                    mock_transaction_repository,
                    mock_withdrawal_request_repository,
                ),
            ]
        )

        service = injector.get(WithdrawalRequestService)
        transaction_service = injector.get(TransactionService)

        with pytest.raises(InvalidAmountException) as exc_info:
            service.approve_withdrawal_request(str(wr.id), transaction_service)
        assert "already approved" in exc_info.value.reason

    def test_reject_withdrawal_request_success(
        self,
        mock_withdrawal_request_repository: MockWithdrawalRequestRepository,
        mock_account_repository: MockAccountRepository,
        mock_transaction_repository: MockTransactionRepository,
        sample_account: Account,
    ):
        """出金リクエスト却下の成功をテスト"""
        mock_account_repository.add(sample_account)

        wr = mock_withdrawal_request_repository.create(
            account_id=str(sample_account.id),
            amount=2000,
            description="To be rejected",
            created_at=datetime.now(UTC),
        )

        injector = Injector(
            [
                RepositoryModule(
                    MockProfileRepository(),
                    mock_account_repository,
                    mock_transaction_repository,
                    mock_withdrawal_request_repository,
                ),
            ]
        )

        service = injector.get(WithdrawalRequestService)

        # テスト
        result = service.reject_withdrawal_request(str(wr.id))

        # 検証
        assert str(result.status) == "rejected"

        # 残高は変わらない
        updated_account = mock_account_repository.get_by_id(str(sample_account.id))
        assert updated_account is not None
        assert int(updated_account.balance) == 10000  # type: ignore[arg-type]

        # トランザクションは作成されない
        transactions = mock_transaction_repository.get_by_account_id(str(sample_account.id))
        assert len(transactions) == 0

    def test_reject_withdrawal_request_not_found(
        self,
        mock_withdrawal_request_repository: MockWithdrawalRequestRepository,
        mock_account_repository: MockAccountRepository,
    ):
        """存在しないリクエストの却下でエラーをテスト"""
        injector = Injector(
            [
                RepositoryModule(
                    MockProfileRepository(),
                    mock_account_repository,
                    MockTransactionRepository(),
                    mock_withdrawal_request_repository,
                ),
            ]
        )

        service = injector.get(WithdrawalRequestService)

        with pytest.raises(ResourceNotFoundException) as exc_info:
            service.reject_withdrawal_request("non-existent-id")
        assert exc_info.value.resource_type == "WithdrawalRequest"

    def test_reject_withdrawal_request_already_processed(
        self,
        mock_withdrawal_request_repository: MockWithdrawalRequestRepository,
        mock_account_repository: MockAccountRepository,
        sample_account: Account,
    ):
        """既に処理済みのリクエスト却下でエラーをテスト"""
        mock_account_repository.add(sample_account)

        wr = mock_withdrawal_request_repository.create(
            account_id=str(sample_account.id),
            amount=1000,
            description="Already rejected",
            created_at=datetime.now(UTC),
        )

        # 先に却下済みに
        mock_withdrawal_request_repository.update_status(wr, "rejected", datetime.now(UTC))

        injector = Injector(
            [
                RepositoryModule(
                    MockProfileRepository(),
                    mock_account_repository,
                    MockTransactionRepository(),
                    mock_withdrawal_request_repository,
                ),
            ]
        )

        service = injector.get(WithdrawalRequestService)

        with pytest.raises(InvalidAmountException) as exc_info:
            service.reject_withdrawal_request(str(wr.id))
        assert "already rejected" in exc_info.value.reason

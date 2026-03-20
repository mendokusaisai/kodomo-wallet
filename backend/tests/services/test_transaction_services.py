"""TransactionService のユニットテスト（家族中心モデル対応）"""

from datetime import UTC, datetime

import pytest
from injector import Injector

from app.core.exceptions import InvalidAmountException, ResourceNotFoundException
from app.domain.entities import Account
from app.repositories.mock_repositories import MockAccountRepository, MockTransactionRepository
from app.services import TransactionService

from .conftest import CHILD_UID, FAMILY_ID, PARENT_UID


class TestTransactionService:
    """TransactionService のテストスイート"""

    def test_get_account_transactions_success(
        self,
        injector_with_mocks: Injector,
        mock_transaction_repository: MockTransactionRepository,
        sample_account: Account,
    ):
        """口座トランザクションの取得成功"""
        mock_transaction_repository.create(
            family_id=FAMILY_ID,
            account_id=sample_account.id,
            transaction_type="deposit",
            amount=1000,
            note="テスト入金",
            created_by_uid=PARENT_UID,
            created_at=datetime.now(UTC),
        )
        service = injector_with_mocks.get(TransactionService)
        results = service.get_account_transactions(FAMILY_ID, sample_account.id)
        assert len(results) == 1

    def test_get_account_transactions_with_limit(
        self,
        injector_with_mocks: Injector,
        mock_transaction_repository: MockTransactionRepository,
        sample_account: Account,
    ):
        """リミット付きトランザクション取得"""
        for i in range(5):
            mock_transaction_repository.create(
                family_id=FAMILY_ID,
                account_id=sample_account.id,
                transaction_type="deposit",
                amount=1000 * (i + 1),
                note=f"Transaction {i + 1}",
                created_by_uid=PARENT_UID,
                created_at=datetime.now(UTC),
            )
        service = injector_with_mocks.get(TransactionService)
        results = service.get_account_transactions(FAMILY_ID, sample_account.id, limit=3)
        assert len(results) == 3

    def test_create_deposit_as_parent_success(
        self,
        injector_with_mocks: Injector,
        mock_account_repository: MockAccountRepository,
        sample_account: Account,
    ):
        """親が入金を作成できる"""
        initial_balance = sample_account.balance
        service = injector_with_mocks.get(TransactionService)
        tx = service.create_deposit(
            family_id=FAMILY_ID,
            account_id=sample_account.id,
            current_uid=PARENT_UID,
            amount=500,
            note="おこづかい",
        )
        assert tx.type == "deposit"
        assert tx.amount == 500
        assert tx.created_by_uid == PARENT_UID
        updated = mock_account_repository.get_by_id(FAMILY_ID, sample_account.id)
        assert updated is not None
        assert updated.balance == initial_balance + 500

    def test_create_deposit_as_child_fails(
        self,
        injector_with_mocks: Injector,
        sample_account: Account,
    ):
        """子供が入金しようとするとエラー"""
        service = injector_with_mocks.get(TransactionService)
        with pytest.raises(InvalidAmountException):
            service.create_deposit(
                family_id=FAMILY_ID,
                account_id=sample_account.id,
                current_uid=CHILD_UID,
                amount=500,
            )

    def test_create_deposit_invalid_amount_fails(
        self,
        injector_with_mocks: Injector,
        sample_account: Account,
    ):
        """金額0以下はエラー"""
        service = injector_with_mocks.get(TransactionService)
        with pytest.raises(InvalidAmountException):
            service.create_deposit(
                family_id=FAMILY_ID,
                account_id=sample_account.id,
                current_uid=PARENT_UID,
                amount=0,
            )

    def test_create_deposit_account_not_found(
        self,
        injector_with_mocks: Injector,
    ):
        """存在しない口座への入金でエラー"""
        service = injector_with_mocks.get(TransactionService)
        with pytest.raises(ResourceNotFoundException):
            service.create_deposit(
                family_id=FAMILY_ID,
                account_id="non-existent",
                current_uid=PARENT_UID,
                amount=500,
            )

    def test_create_withdraw_as_parent_success(
        self,
        injector_with_mocks: Injector,
        mock_account_repository: MockAccountRepository,
        sample_account: Account,
    ):
        """親が出金を作成できる"""
        initial_balance = sample_account.balance
        service = injector_with_mocks.get(TransactionService)
        tx = service.create_withdraw(
            family_id=FAMILY_ID,
            account_id=sample_account.id,
            current_uid=PARENT_UID,
            amount=3000,
            note="おこづかい引き出し",
        )
        assert tx.type == "withdraw"
        assert tx.amount == 3000
        updated = mock_account_repository.get_by_id(FAMILY_ID, sample_account.id)
        assert updated is not None
        assert updated.balance == initial_balance - 3000

    def test_create_withdraw_insufficient_balance(
        self,
        injector_with_mocks: Injector,
        sample_account: Account,
    ):
        """残高不足で出金エラー"""
        service = injector_with_mocks.get(TransactionService)
        with pytest.raises(InvalidAmountException):
            service.create_withdraw(
                family_id=FAMILY_ID,
                account_id=sample_account.id,
                current_uid=PARENT_UID,
                amount=99999,
            )

"""RecurringDepositService のユニットテスト（家族中心モデル対応）"""

from datetime import UTC, datetime, timedelta

import pytest
from injector import Injector

from app.core.exceptions import InvalidAmountException, ResourceNotFoundException
from app.domain.entities import Account
from app.repositories.mock_repositories import MockRecurringDepositRepository
from app.services import RecurringDepositService

from .conftest import CHILD_UID, FAMILY_ID, PARENT_UID


class TestRecurringDepositService:
    """RecurringDepositService のテストスイート"""

    def test_get_recurring_deposit_none(
        self,
        injector_with_mocks: Injector,
        sample_account: Account,
    ):
        """定期入金が未設定の場合は None を返す"""
        service = injector_with_mocks.get(RecurringDepositService)
        result = service.get_recurring_deposit(FAMILY_ID, sample_account.id)
        assert result is None

    def test_create_recurring_deposit_as_parent_success(
        self,
        injector_with_mocks: Injector,
        mock_recurring_deposit_repository: MockRecurringDepositRepository,
        sample_account: Account,
    ):
        """親が定期入金を設定できる"""
        service = injector_with_mocks.get(RecurringDepositService)
        rd = service.create_or_update_recurring_deposit(
            family_id=FAMILY_ID,
            account_id=sample_account.id,
            current_uid=PARENT_UID,
            amount=1000,
            interval_days=7,
        )
        assert rd.family_id == FAMILY_ID
        assert rd.account_id == sample_account.id
        assert rd.amount == 1000
        assert rd.interval_days == 7
        assert rd.created_by_uid == PARENT_UID

    def test_create_recurring_deposit_as_child_fails(
        self,
        injector_with_mocks: Injector,
        sample_account: Account,
    ):
        """子供が定期入金を設定しようとするとエラー"""
        service = injector_with_mocks.get(RecurringDepositService)
        with pytest.raises(InvalidAmountException):
            service.create_or_update_recurring_deposit(
                family_id=FAMILY_ID,
                account_id=sample_account.id,
                current_uid=CHILD_UID,
                amount=1000,
                interval_days=7,
            )

    def test_create_recurring_deposit_invalid_amount_fails(
        self,
        injector_with_mocks: Injector,
        sample_account: Account,
    ):
        """金額0以下はエラー"""
        service = injector_with_mocks.get(RecurringDepositService)
        with pytest.raises(InvalidAmountException):
            service.create_or_update_recurring_deposit(
                family_id=FAMILY_ID,
                account_id=sample_account.id,
                current_uid=PARENT_UID,
                amount=0,
                interval_days=7,
            )

    def test_create_recurring_deposit_invalid_interval_fails(
        self,
        injector_with_mocks: Injector,
        sample_account: Account,
    ):
        """interval_days が0以下はエラー"""
        service = injector_with_mocks.get(RecurringDepositService)
        with pytest.raises(InvalidAmountException):
            service.create_or_update_recurring_deposit(
                family_id=FAMILY_ID,
                account_id=sample_account.id,
                current_uid=PARENT_UID,
                amount=1000,
                interval_days=0,
            )

    def test_update_recurring_deposit_as_parent_success(
        self,
        injector_with_mocks: Injector,
        sample_account: Account,
    ):
        """親が定期入金を更新できる"""
        service = injector_with_mocks.get(RecurringDepositService)
        service.create_or_update_recurring_deposit(
            family_id=FAMILY_ID,
            account_id=sample_account.id,
            current_uid=PARENT_UID,
            amount=500,
            interval_days=30,
        )
        updated = service.create_or_update_recurring_deposit(
            family_id=FAMILY_ID,
            account_id=sample_account.id,
            current_uid=PARENT_UID,
            amount=2000,
            interval_days=14,
        )
        assert updated.amount == 2000
        assert updated.interval_days == 14

    def test_delete_recurring_deposit_as_parent_success(
        self,
        injector_with_mocks: Injector,
        sample_account: Account,
    ):
        """親が定期入金を削除できる"""
        service = injector_with_mocks.get(RecurringDepositService)
        service.create_or_update_recurring_deposit(
            family_id=FAMILY_ID,
            account_id=sample_account.id,
            current_uid=PARENT_UID,
            amount=1000,
            interval_days=7,
        )
        service.delete_recurring_deposit(
            family_id=FAMILY_ID,
            account_id=sample_account.id,
            current_uid=PARENT_UID,
        )
        result = service.get_recurring_deposit(FAMILY_ID, sample_account.id)
        assert result is None

    def test_delete_recurring_deposit_as_child_fails(
        self,
        injector_with_mocks: Injector,
        sample_account: Account,
    ):
        """子供が定期入金を削除しようとするとエラー"""
        service = injector_with_mocks.get(RecurringDepositService)
        service.create_or_update_recurring_deposit(
            family_id=FAMILY_ID,
            account_id=sample_account.id,
            current_uid=PARENT_UID,
            amount=1000,
            interval_days=7,
        )
        with pytest.raises(InvalidAmountException):
            service.delete_recurring_deposit(
                family_id=FAMILY_ID,
                account_id=sample_account.id,
                current_uid=CHILD_UID,
            )

    def test_delete_recurring_deposit_not_found(
        self,
        injector_with_mocks: Injector,
        sample_account: Account,
    ):
        """設定されていない定期入金の削除でエラー"""
        service = injector_with_mocks.get(RecurringDepositService)
        with pytest.raises(ResourceNotFoundException):
            service.delete_recurring_deposit(
                family_id=FAMILY_ID,
                account_id=sample_account.id,
                current_uid=PARENT_UID,
            )

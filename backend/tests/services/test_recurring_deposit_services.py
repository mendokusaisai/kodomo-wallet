"""RecurringDepositService のユニットテスト"""

import uuid
from datetime import UTC, datetime

import pytest
from injector import Injector

from app.core.exceptions import InvalidAmountException, ResourceNotFoundException
from app.domain.entities import Account, Profile
from app.repositories.mock_repositories import (
    MockAccountRepository,
    MockProfileRepository,
    MockRecurringDepositRepository,
    MockTransactionRepository,
    MockWithdrawalRequestRepository,
)
from app.services import RecurringDepositService

from .conftest import RepositoryModule


class TestRecurringDepositService:
    """RecurringDepositService のビジネスロジックをテスト"""

    def test_get_recurring_deposit_by_parent(
        self,
        mock_profile_repository: MockProfileRepository,
        mock_account_repository: MockAccountRepository,
        mock_recurring_deposit_repository: MockRecurringDepositRepository,
        sample_profile: Profile,
        sample_child: Profile,
        sample_account: Account,
    ):
        """親が子供の定期入金設定を取得できることをテスト"""
        # プロフィールとアカウントを準備
        mock_profile_repository.add(sample_profile)
        sample_child.parent_id = sample_profile.id
        mock_profile_repository.add(sample_child)
        sample_account.user_id = sample_child.id
        mock_account_repository.add(sample_account)

        # 定期入金設定を作成
        rd = mock_recurring_deposit_repository.create(
            account_id=str(sample_account.id),
            amount=5000,
            day_of_month=15,
            created_at=datetime.now(UTC),
        )

        injector = Injector(
            [
                RepositoryModule(
                    mock_profile_repository,
                    mock_account_repository,
                    MockTransactionRepository(),
                    MockWithdrawalRequestRepository(),
                    mock_recurring_deposit_repository,
                ),
            ]
        )

        service = injector.get(RecurringDepositService)

        # 親が子供のアカウントの定期入金設定を取得
        result = service.get_recurring_deposit(str(sample_account.id), str(sample_profile.id))

        assert result is not None
        assert result.id == rd.id
        assert result.amount == 5000

    def test_get_recurring_deposit_account_not_found(
        self,
        mock_profile_repository: MockProfileRepository,
        mock_account_repository: MockAccountRepository,
        mock_recurring_deposit_repository: MockRecurringDepositRepository,
    ):
        """存在しないアカウントの定期入金設定を取得しようとするとエラーになることをテスト"""
        injector = Injector(
            [
                RepositoryModule(
                    mock_profile_repository,
                    mock_account_repository,
                    MockTransactionRepository(),
                    MockWithdrawalRequestRepository(),
                    mock_recurring_deposit_repository,
                ),
            ]
        )

        service = injector.get(RecurringDepositService)

        with pytest.raises(ResourceNotFoundException) as exc_info:
            service.get_recurring_deposit(str(uuid.uuid4()), str(uuid.uuid4()))
        assert "Account" in str(exc_info.value)

    def test_create_or_update_recurring_deposit_create_new(
        self,
        mock_profile_repository: MockProfileRepository,
        mock_account_repository: MockAccountRepository,
        mock_recurring_deposit_repository: MockRecurringDepositRepository,
        sample_profile: Profile,
        sample_child: Profile,
        sample_account: Account,
    ):
        """新しい定期入金設定を作成できることをテスト"""
        # プロフィールとアカウントを準備
        mock_profile_repository.add(sample_profile)
        sample_child.parent_id = sample_profile.id
        mock_profile_repository.add(sample_child)
        sample_account.user_id = sample_child.id
        mock_account_repository.add(sample_account)

        injector = Injector(
            [
                RepositoryModule(
                    mock_profile_repository,
                    mock_account_repository,
                    MockTransactionRepository(),
                    MockWithdrawalRequestRepository(),
                    mock_recurring_deposit_repository,
                ),
            ]
        )

        service = injector.get(RecurringDepositService)

        # 親が子供のアカウントに定期入金設定を作成
        result = service.create_or_update_recurring_deposit(
            account_id=str(sample_account.id),
            current_user_id=str(sample_profile.id),
            amount=3000,
            day_of_month=1,
            is_active=True,
        )

        assert result is not None
        assert result.amount == 3000
        assert result.day_of_month == 1
        assert result.is_active is True

    def test_create_or_update_recurring_deposit_update_existing(
        self,
        mock_profile_repository: MockProfileRepository,
        mock_account_repository: MockAccountRepository,
        mock_recurring_deposit_repository: MockRecurringDepositRepository,
        sample_profile: Profile,
        sample_child: Profile,
        sample_account: Account,
    ):
        """既存の定期入金設定を更新できることをテスト"""
        # プロフィールとアカウントを準備
        mock_profile_repository.add(sample_profile)
        sample_child.parent_id = sample_profile.id
        mock_profile_repository.add(sample_child)
        sample_account.user_id = sample_child.id
        mock_account_repository.add(sample_account)

        # 既存の定期入金設定を作成
        existing = mock_recurring_deposit_repository.create(
            account_id=str(sample_account.id),
            amount=5000,
            day_of_month=15,
            created_at=datetime.now(UTC),
        )

        injector = Injector(
            [
                RepositoryModule(
                    mock_profile_repository,
                    mock_account_repository,
                    MockTransactionRepository(),
                    MockWithdrawalRequestRepository(),
                    mock_recurring_deposit_repository,
                ),
            ]
        )

        service = injector.get(RecurringDepositService)

        # 親が子供のアカウントの定期入金設定を更新
        result = service.create_or_update_recurring_deposit(
            account_id=str(sample_account.id),
            current_user_id=str(sample_profile.id),
            amount=10000,
            day_of_month=25,
            is_active=False,
        )

        assert result is not None
        assert result.id == existing.id
        assert result.amount == 10000
        assert result.day_of_month == 25
        assert result.is_active is False

    def test_create_or_update_recurring_deposit_with_invalid_amount(
        self,
        mock_profile_repository: MockProfileRepository,
        mock_account_repository: MockAccountRepository,
        mock_recurring_deposit_repository: MockRecurringDepositRepository,
        sample_profile: Profile,
        sample_child: Profile,
        sample_account: Account,
    ):
        """不正な金額で定期入金設定を作成しようとするとエラーになることをテスト"""
        # プロフィールとアカウントを準備
        mock_profile_repository.add(sample_profile)
        sample_child.parent_id = sample_profile.id
        mock_profile_repository.add(sample_child)
        sample_account.user_id = sample_child.id
        mock_account_repository.add(sample_account)

        injector = Injector(
            [
                RepositoryModule(
                    mock_profile_repository,
                    mock_account_repository,
                    MockTransactionRepository(),
                    MockWithdrawalRequestRepository(),
                    mock_recurring_deposit_repository,
                ),
            ]
        )

        service = injector.get(RecurringDepositService)

        # 負の金額
        with pytest.raises(InvalidAmountException) as exc_info:
            service.create_or_update_recurring_deposit(
                account_id=str(sample_account.id),
                current_user_id=str(sample_profile.id),
                amount=-100,
                day_of_month=1,
            )
        assert "positive" in exc_info.value.reason

        # ゼロの金額
        with pytest.raises(InvalidAmountException) as exc_info:
            service.create_or_update_recurring_deposit(
                account_id=str(sample_account.id),
                current_user_id=str(sample_profile.id),
                amount=0,
                day_of_month=1,
            )
        assert "positive" in exc_info.value.reason

    def test_create_or_update_recurring_deposit_with_invalid_day(
        self,
        mock_profile_repository: MockProfileRepository,
        mock_account_repository: MockAccountRepository,
        mock_recurring_deposit_repository: MockRecurringDepositRepository,
        sample_profile: Profile,
        sample_child: Profile,
        sample_account: Account,
    ):
        """不正な日付で定期入金設定を作成しようとするとエラーになることをテスト"""
        # プロフィールとアカウントを準備
        mock_profile_repository.add(sample_profile)
        sample_child.parent_id = sample_profile.id
        mock_profile_repository.add(sample_child)
        sample_account.user_id = sample_child.id
        mock_account_repository.add(sample_account)

        injector = Injector(
            [
                RepositoryModule(
                    mock_profile_repository,
                    mock_account_repository,
                    MockTransactionRepository(),
                    MockWithdrawalRequestRepository(),
                    mock_recurring_deposit_repository,
                ),
            ]
        )

        service = injector.get(RecurringDepositService)

        # 範囲外の日付（0）
        with pytest.raises(InvalidAmountException) as exc_info:
            service.create_or_update_recurring_deposit(
                account_id=str(sample_account.id),
                current_user_id=str(sample_profile.id),
                amount=5000,
                day_of_month=0,
            )
        assert "between 1 and 31" in exc_info.value.reason

        # 範囲外の日付（32）
        with pytest.raises(InvalidAmountException) as exc_info:
            service.create_or_update_recurring_deposit(
                account_id=str(sample_account.id),
                current_user_id=str(sample_profile.id),
                amount=5000,
                day_of_month=32,
            )
        assert "between 1 and 31" in exc_info.value.reason

    def test_delete_recurring_deposit_success(
        self,
        mock_profile_repository: MockProfileRepository,
        mock_account_repository: MockAccountRepository,
        mock_recurring_deposit_repository: MockRecurringDepositRepository,
        sample_profile: Profile,
        sample_child: Profile,
        sample_account: Account,
    ):
        """定期入金設定を削除できることをテスト"""
        # プロフィールとアカウントを準備
        mock_profile_repository.add(sample_profile)
        sample_child.parent_id = sample_profile.id
        mock_profile_repository.add(sample_child)
        sample_account.user_id = sample_child.id
        mock_account_repository.add(sample_account)

        # 定期入金設定を作成
        mock_recurring_deposit_repository.create(
            account_id=str(sample_account.id),
            amount=5000,
            day_of_month=15,
            created_at=datetime.now(UTC),
        )

        injector = Injector(
            [
                RepositoryModule(
                    mock_profile_repository,
                    mock_account_repository,
                    MockTransactionRepository(),
                    MockWithdrawalRequestRepository(),
                    mock_recurring_deposit_repository,
                ),
            ]
        )

        service = injector.get(RecurringDepositService)

        # 親が子供のアカウントの定期入金設定を削除
        result = service.delete_recurring_deposit(
            account_id=str(sample_account.id), current_user_id=str(sample_profile.id)
        )

        assert result is True

        # 削除後は取得できない
        deleted = service.get_recurring_deposit(str(sample_account.id), str(sample_profile.id))
        assert deleted is None

    def test_delete_recurring_deposit_not_found(
        self,
        mock_profile_repository: MockProfileRepository,
        mock_account_repository: MockAccountRepository,
        mock_recurring_deposit_repository: MockRecurringDepositRepository,
        sample_profile: Profile,
        sample_child: Profile,
        sample_account: Account,
    ):
        """存在しない定期入金設定を削除しようとするとエラーになることをテスト"""
        # プロフィールとアカウントを準備
        mock_profile_repository.add(sample_profile)
        sample_child.parent_id = sample_profile.id
        mock_profile_repository.add(sample_child)
        sample_account.user_id = sample_child.id
        mock_account_repository.add(sample_account)

        injector = Injector(
            [
                RepositoryModule(
                    mock_profile_repository,
                    mock_account_repository,
                    MockTransactionRepository(),
                    MockWithdrawalRequestRepository(),
                    mock_recurring_deposit_repository,
                ),
            ]
        )

        service = injector.get(RecurringDepositService)

        with pytest.raises(ResourceNotFoundException) as exc_info:
            service.delete_recurring_deposit(
                account_id=str(sample_account.id), current_user_id=str(sample_profile.id)
            )
        assert "RecurringDeposit" in str(exc_info.value)

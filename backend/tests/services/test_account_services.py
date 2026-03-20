"""AccountService のユニットテスト（家族中心モデル対応）"""

import pytest
from injector import Injector

from app.core.exceptions import InvalidAmountException, ResourceNotFoundException
from app.domain.entities import Account
from app.repositories.mock_repositories import MockAccountRepository
from app.services import AccountService

from .conftest import CHILD_UID, FAMILY_ID, PARENT_UID


class TestAccountService:
    """AccountService のテストスイート"""

    def test_get_family_accounts_success(
        self,
        injector_with_mocks: Injector,
        sample_account: Account,
    ):
        """家族の口座一覧取得成功"""
        service = injector_with_mocks.get(AccountService)
        results = service.get_family_accounts(FAMILY_ID)
        assert len(results) == 1
        assert results[0].id == sample_account.id

    def test_get_family_accounts_empty(
        self,
        injector_with_mocks: Injector,
    ):
        """口座のない家族の場合は空リスト"""
        service = injector_with_mocks.get(AccountService)
        results = service.get_family_accounts("other-family-id")
        assert results == []

    def test_create_account_as_parent_success(
        self,
        injector_with_mocks: Injector,
        mock_account_repository: MockAccountRepository,
    ):
        """親が口座作成できる"""
        service = injector_with_mocks.get(AccountService)
        account = service.create_account(
            family_id=FAMILY_ID,
            name="旅行貯金",
            current_uid=PARENT_UID,
        )
        assert account.family_id == FAMILY_ID
        assert account.name == "旅行貯金"
        assert account.balance == 0
        stored = mock_account_repository.get_by_id(FAMILY_ID, account.id)
        assert stored is not None

    def test_create_account_as_child_fails(
        self,
        injector_with_mocks: Injector,
    ):
        """子供が口座作成しようとするとエラー"""
        service = injector_with_mocks.get(AccountService)
        with pytest.raises(InvalidAmountException):
            service.create_account(
                family_id=FAMILY_ID,
                name="子供の口座",
                current_uid=CHILD_UID,
            )

    def test_update_goal_as_parent_success(
        self,
        injector_with_mocks: Injector,
        mock_account_repository: MockAccountRepository,
        sample_account: Account,
    ):
        """親が目標を設定できる"""
        service = injector_with_mocks.get(AccountService)
        updated = service.update_goal(
            family_id=FAMILY_ID,
            account_id=sample_account.id,
            current_uid=PARENT_UID,
            goal_name="新しいゲーム機",
            goal_amount=50000,
        )
        assert updated.goal_name == "新しいゲーム機"
        assert updated.goal_amount == 50000

    def test_update_goal_as_child_fails(
        self,
        injector_with_mocks: Injector,
        sample_account: Account,
    ):
        """子供が目標を変更しようとするとエラー"""
        service = injector_with_mocks.get(AccountService)
        with pytest.raises(InvalidAmountException):
            service.update_goal(
                family_id=FAMILY_ID,
                account_id=sample_account.id,
                current_uid=CHILD_UID,
                goal_name="ゲーム機",
                goal_amount=30000,
            )

    def test_update_goal_negative_amount_fails(
        self,
        injector_with_mocks: Injector,
        sample_account: Account,
    ):
        """負の目標金額はエラー"""
        service = injector_with_mocks.get(AccountService)
        with pytest.raises(InvalidAmountException):
            service.update_goal(
                family_id=FAMILY_ID,
                account_id=sample_account.id,
                current_uid=PARENT_UID,
                goal_name="目標",
                goal_amount=-1000,
            )

    def test_update_goal_account_not_found(
        self,
        injector_with_mocks: Injector,
    ):
        """存在しない口座の目標更新でエラー"""
        service = injector_with_mocks.get(AccountService)
        with pytest.raises(ResourceNotFoundException):
            service.update_goal(
                family_id=FAMILY_ID,
                account_id="non-existent",
                current_uid=PARENT_UID,
                goal_name="目標",
                goal_amount=10000,
            )

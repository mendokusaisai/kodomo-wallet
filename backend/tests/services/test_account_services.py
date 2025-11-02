"""
AccountServiceのテスト
"""

import uuid
from datetime import UTC, datetime

import pytest
from injector import Injector

from app.domain.entities import Account, Profile
from app.repositories.mock_repositories import (
    MockAccountRepository,
    MockFamilyRelationshipRepository,
    MockProfileRepository,
)
from app.services import AccountService


class TestAccountService:
    """AccountService のテストスイート"""

    def test_get_user_accounts_success(
        self,
        injector_with_mocks: Injector,
        mock_account_repository: MockAccountRepository,
        sample_profile: Profile,
    ):
        """ユーザーアカウントの取得成功をテスト"""
        # 準備: モックリポジトリにアカウントを追加
        account1 = Account(
            id="sample-id-1",
            user_id=sample_profile.id,
            balance=5000,
            currency="JPY",
            goal_amount=10000,
            goal_name="Vacation",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        account2 = Account(
            id="sample-id-2",
            user_id=sample_profile.id,
            balance=3000,
            currency="JPY",
            goal_amount=5000,
            goal_name="Gadgets",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        mock_account_repository.add(account1)
        mock_account_repository.add(account2)

        # テスト: サービスを取得してアカウントを取得
        service = injector_with_mocks.get(AccountService)
        results = service.get_user_accounts(sample_profile.id)

        # 検証
        assert len(results) == 2
        assert all(acc.user_id == sample_profile.id for acc in results)

    def test_get_user_accounts_empty(self, injector_with_mocks: Injector):
        """アカウントを持たないユーザーのアカウント取得をテスト"""
        service = injector_with_mocks.get(AccountService)
        results = service.get_user_accounts("non-existent-user")

        assert results == []

    def test_get_user_accounts_filters_by_user_id(
        self, injector_with_mocks: Injector, mock_account_repository: MockAccountRepository
    ):
        """指定したユーザーのアカウントのみが返されることをテスト"""
        # 準備: 異なるユーザーのアカウントを追加
        user1_id = uuid.uuid4()
        user2_id = uuid.uuid4()

        account1 = Account(
            id=str(uuid.uuid4()),
            user_id=str(user1_id),
            balance=1000,
            currency="JPY",
            goal_name=None,
            goal_amount=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        account2 = Account(
            id=str(uuid.uuid4()),
            user_id=str(user2_id),
            balance=2000,
            currency="JPY",
            goal_name=None,
            goal_amount=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        account3 = Account(
            id=str(uuid.uuid4()),
            user_id=str(user1_id),
            balance=3000,
            currency="JPY",
            goal_name=None,
            goal_amount=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        mock_account_repository.add(account1)
        mock_account_repository.add(account2)
        mock_account_repository.add(account3)

        # テスト: user1のアカウントを取得
        service = injector_with_mocks.get(AccountService)
        results = service.get_user_accounts(str(user1_id))

        # 検証: user1のアカウントのみが返される
        assert len(results) == 2
        assert all(acc.user_id == str(user1_id) for acc in results)

    def test_get_family_accounts_as_parent(
        self,
        injector_with_mocks: Injector,
        mock_account_repository: MockAccountRepository,
        mock_profile_repository: MockProfileRepository,
        mock_family_relationship_repository: MockFamilyRelationshipRepository,
        sample_profile: Profile,
        sample_child,
    ):
        """親ユーザーが子供のアカウントを取得することをテスト"""
        # 準備: 親と子のプロフィール、子のアカウントを設定
        sample_profile.role = "parent"
        mock_profile_repository.add(sample_profile)

        sample_child.role = "child"
        mock_profile_repository.add(sample_child)
        mock_profile_repository.add_relationship(sample_profile.id, sample_child.id)

        child_account = Account(
            id=str(uuid.uuid4()),
            user_id=sample_child.id,
            balance=5000,
            currency="JPY",
            goal_name="ゲーム機",
            goal_amount=30000,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        mock_account_repository.add(child_account)

        # テスト: 親が家族アカウントを取得
        service = injector_with_mocks.get(AccountService)
        results = service.get_family_accounts(sample_profile.id)

        # 検証: 子供のアカウントのみが返される
        assert len(results) == 1
        assert results[0].user_id == sample_child.id

    def test_get_family_accounts_as_child(
        self,
        injector_with_mocks: Injector,
        mock_account_repository: MockAccountRepository,
        mock_profile_repository,
        sample_child,
    ):
        """子ユーザーが自分のアカウントを取得することをテスト"""
        # 準備: 子のプロフィールとアカウントを設定
        sample_child.role = "child"
        mock_profile_repository.add(sample_child)

        child_account = Account(
            id=str(uuid.uuid4()),
            user_id=sample_child.id,
            balance=3000,
            currency="JPY",
            goal_name="おもちゃ",
            goal_amount=5000,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        mock_account_repository.add(child_account)

        # テスト: 子が家族アカウントを取得
        service = injector_with_mocks.get(AccountService)
        results = service.get_family_accounts(sample_child.id)

        # 検証: 自分のアカウントが返される
        assert len(results) == 1
        assert results[0].user_id == sample_child.id

    def test_get_family_accounts_parent_with_multiple_children(
        self,
        injector_with_mocks: Injector,
        mock_account_repository: MockAccountRepository,
        mock_profile_repository: MockProfileRepository,
        sample_profile: Profile,
    ):
        """親ユーザーが複数の子供のアカウントを取得することをテスト"""
        # 準備: 親と2人の子、それぞれのアカウントを設定
        sample_profile.role = "parent"
        mock_profile_repository.add(sample_profile)

        child1 = Profile(
            id=str(uuid.uuid4()),
            name="子供1",
            role="child",
            email=None,
            auth_user_id=None,
            avatar_url=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        child2 = Profile(
            id=str(uuid.uuid4()),
            name="子供2",
            role="child",
            email=None,
            auth_user_id=None,
            avatar_url=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        mock_profile_repository.add(child1)
        mock_profile_repository.add(child2)
        mock_profile_repository.add_relationship(sample_profile.id, child1.id)
        mock_profile_repository.add_relationship(sample_profile.id, child2.id)

        account1 = Account(
            id=str(uuid.uuid4()),
            user_id=child1.id,
            balance=5000,
            currency="JPY",
            goal_name="ゲーム",
            goal_amount=10000,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        account2 = Account(
            id=str(uuid.uuid4()),
            user_id=child2.id,
            balance=3000,
            currency="JPY",
            goal_name="おもちゃ",
            goal_amount=8000,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        mock_account_repository.add(account1)
        mock_account_repository.add(account2)

        # テスト: 親が家族アカウントを取得
        service = injector_with_mocks.get(AccountService)
        results = service.get_family_accounts(sample_profile.id)

        # 検証: 両方の子供のアカウントが返される
        assert len(results) == 2
        user_ids = {acc.user_id for acc in results}
        assert child1.id in user_ids
        assert child2.id in user_ids

    def test_update_goal_success(
        self,
        injector_with_mocks: Injector,
        mock_account_repository: MockAccountRepository,
        sample_profile: Profile,
    ):
        """アカウントの目標更新成功をテスト"""
        # 準備: アカウントを作成
        account = Account(
            id=str(uuid.uuid4()),
            user_id=sample_profile.id,
            balance=10000,
            currency="JPY",
            goal_name=None,
            goal_amount=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        mock_account_repository.add(account)

        # テスト: 目標を設定
        service = injector_with_mocks.get(AccountService)
        updated = service.update_goal(account.id, "新しいゲーム機", 50000)

        # 検証
        assert updated.goal_name == "新しいゲーム機"
        assert updated.goal_amount == 50000

    def test_update_goal_clear_goal(
        self,
        injector_with_mocks: Injector,
        mock_account_repository: MockAccountRepository,
        sample_profile: Profile,
    ):
        """アカウントの目標クリアをテスト"""
        # 準備: 目標を持つアカウントを作成
        account = Account(
            id=str(uuid.uuid4()),
            user_id=sample_profile.id,
            balance=10000,
            currency="JPY",
            goal_name="古い目標",
            goal_amount=20000,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        mock_account_repository.add(account)

        # テスト: 目標をクリア
        service = injector_with_mocks.get(AccountService)
        updated = service.update_goal(account.id, None, None)

        # 検証
        assert updated.goal_name is None
        assert updated.goal_amount is None

    def test_update_goal_account_not_found(self, injector_with_mocks: Injector):
        """存在しないアカウントの目標更新でエラーをテスト"""
        from app.core.exceptions import ResourceNotFoundException

        service = injector_with_mocks.get(AccountService)

        # テスト: 存在しないアカウントの目標を更新
        with pytest.raises(ResourceNotFoundException) as exc_info:
            service.update_goal("non-existent-id", "目標", 10000)

        # 検証
        assert exc_info.value.resource_type == "Account"
        assert exc_info.value.resource_id == "non-existent-id"

    def test_update_goal_negative_amount(
        self,
        injector_with_mocks: Injector,
        mock_account_repository: MockAccountRepository,
        sample_profile: Profile,
    ):
        """負の金額での目標更新でエラーをテスト"""
        from app.core.exceptions import InvalidAmountException

        # 準備: アカウントを作成
        account = Account(
            id=str(uuid.uuid4()),
            user_id=sample_profile.id,
            balance=10000,
            currency="JPY",
            goal_name=None,
            goal_amount=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        mock_account_repository.add(account)

        # テスト: 負の金額で目標を設定
        service = injector_with_mocks.get(AccountService)
        with pytest.raises(InvalidAmountException) as exc_info:
            service.update_goal(account.id, "目標", -1000)

        # 検証
        assert exc_info.value.amount == -1000
        assert "non-negative" in exc_info.value.reason

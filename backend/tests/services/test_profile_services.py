"""ProfileService のユニットテスト"""

import uuid
from dataclasses import replace

import pytest
from injector import Injector

from app.core.exceptions import InvalidAmountException
from app.domain.entities import Profile
from app.repositories.mock_repositories import (
    MockAccountRepository,
    MockProfileRepository,
    MockTransactionRepository,
)
from app.services import ProfileService

from .conftest import RepositoryModule


class TestProfileService:
    """ProfileService のテストスイート"""

    def test_get_profile_success(
        self,
        injector_with_mocks: Injector,
        mock_profile_repository: MockProfileRepository,
        sample_profile: Profile,
    ):
        """プロフィール取得の成功をテスト"""
        # Setup: モックリポジトリにプロフィールを追加
        mock_profile_repository.add(sample_profile)

        # Test: サービスを取得してプロフィールを取得
        service = injector_with_mocks.get(ProfileService)
        result = service.get_profile(str(sample_profile.id))

        # Verify
        assert result is not None
        assert result.id == sample_profile.id
        assert result.name == "Test User"
        assert result.role == "parent"

    def test_get_profile_not_found(self, injector_with_mocks: Injector):
        """存在しないプロフィールの取得をテスト"""
        service = injector_with_mocks.get(ProfileService)
        result = service.get_profile("non-existent-id")

        assert result is None

    def test_get_profile_uses_repository(
        self,
        mock_profile_repository: MockProfileRepository,
        mock_account_repository: MockAccountRepository,
        mock_transaction_repository: MockTransactionRepository,
        sample_profile: Profile,
    ):
        """ProfileServiceが注入されたリポジトリを使用することをテスト"""
        # 準備: 特定のリポジトリを持つサービスを作成
        mock_profile_repository.add(sample_profile)

        injector = Injector(
            [
                RepositoryModule(
                    mock_profile_repository,
                    mock_account_repository,
                    mock_transaction_repository,
                ),
            ]
        )

        service = injector.get(ProfileService)

        # テスト
        result = service.get_profile(str(sample_profile.id))

        # 検証: 同じリポジトリインスタンスであることを確認
        assert result is not None
        assert result == sample_profile

    def test_get_children_success(
        self,
        injector_with_mocks: Injector,
        mock_profile_repository: MockProfileRepository,
        mock_family_relationship_repository,
        sample_profile: Profile,
        sample_child: Profile,
    ):
        """親の子供リスト取得の成功をテスト"""
        # 準備: 親と子をリポジトリに追加
        mock_profile_repository.add(sample_profile)
        mock_profile_repository.add(sample_child)
        mock_family_relationship_repository.add_relationship(sample_profile.id, sample_child.id)

        # テスト
        service = injector_with_mocks.get(ProfileService)
        children = service.get_children(sample_profile.id)

        # 検証
        assert len(children) == 1
        assert children[0].id == sample_child.id

    def test_get_children_empty(self, injector_with_mocks: Injector, sample_profile: Profile):
        """子供がいない親の子供リスト取得をテスト"""
        # テスト
        service = injector_with_mocks.get(ProfileService)
        children = service.get_children(sample_profile.id)

        # 検証
        assert len(children) == 0

    def test_get_by_auth_user_id_success(
        self,
        injector_with_mocks: Injector,
        mock_profile_repository: MockProfileRepository,
        sample_profile: Profile,
    ):
        """認証ユーザーIDでプロフィール取得の成功をテスト"""
        # 準備
        import uuid

        auth_id = str(uuid.uuid4())
        from dataclasses import replace

        profile_with_auth = replace(sample_profile, auth_user_id=auth_id)
        mock_profile_repository.add(profile_with_auth)

        # テスト
        service = injector_with_mocks.get(ProfileService)
        result = service.get_by_auth_user_id(auth_id)

        # 検証
        assert result is not None
        assert result.auth_user_id == auth_id
        assert result.id == sample_profile.id

    def test_get_by_auth_user_id_not_found(self, injector_with_mocks: Injector):
        """存在しない認証ユーザーIDでプロフィール取得をテスト"""
        # テスト
        service = injector_with_mocks.get(ProfileService)
        result = service.get_by_auth_user_id("non-existent-auth-id")

        # 検証
        assert result is None

    def test_create_child_success(
        self,
        injector_with_mocks: Injector,
        mock_profile_repository: MockProfileRepository,
        mock_account_repository,
        mock_family_relationship_repository,
        sample_profile: Profile,
    ):
        """子供プロフィール作成の成功をテスト"""
        # 準備: 親プロフィールを追加
        sample_profile.role = "parent"
        mock_profile_repository.add(sample_profile)

        # テスト
        service = injector_with_mocks.get(ProfileService)
        child = service.create_child(
            parent_id=sample_profile.id,
            child_name="新しい子供",
            initial_balance=1000,
        )

        # 検証
        assert child.name == "新しい子供"
        assert child.role == "child"
        # 親子関係が作成されていること
        assert mock_family_relationship_repository.has_relationship(sample_profile.id, child.id)

        # アカウントも作成されたことを確認
        accounts = mock_account_repository.get_by_user_id(child.id)
        assert len(accounts) == 1
        assert accounts[0].balance == 1000

    def test_create_child_parent_not_found(self, injector_with_mocks: Injector):
        """存在しない親で子供プロフィール作成をテスト"""
        from app.core.exceptions import ResourceNotFoundException

        # テスト
        service = injector_with_mocks.get(ProfileService)

        with pytest.raises(ResourceNotFoundException) as exc_info:
            service.create_child(
                parent_id="non-existent-parent",
                child_name="新しい子供",
            )

        # 検証
        assert exc_info.value.resource_type == "Parent"

    def test_create_child_invalid_parent_role(
        self,
        injector_with_mocks: Injector,
        mock_profile_repository: MockProfileRepository,
        sample_child: Profile,
    ):
        """子供ロールのユーザーで子供プロフィール作成をテスト"""
        from app.core.exceptions import ResourceNotFoundException

        # 準備: 子供プロフィールを追加
        sample_child.role = "child"
        mock_profile_repository.add(sample_child)

        # テスト
        service = injector_with_mocks.get(ProfileService)

        with pytest.raises(ResourceNotFoundException) as exc_info:
            service.create_child(
                parent_id=sample_child.id,
                child_name="新しい子供",
            )

        # 検証
        assert exc_info.value.resource_type == "Parent"

    def test_delete_child_success(
        self,
        injector_with_mocks: Injector,
        mock_profile_repository: MockProfileRepository,
        mock_account_repository: MockAccountRepository,
        mock_family_relationship_repository,
        sample_profile: Profile,
        sample_child: Profile,
    ):
        """子供プロフィール削除の成功をテスト"""
        import uuid
        from datetime import UTC, datetime

        from app.domain.entities import Account

        # 準備: 親と子、子のアカウントを追加
        sample_profile.role = "parent"
        mock_profile_repository.add(sample_profile)

        sample_child.role = "child"
        mock_profile_repository.add(sample_child)
        mock_family_relationship_repository.add_relationship(sample_profile.id, sample_child.id)

        child_account = Account(
            id=str(uuid.uuid4()),
            user_id=sample_child.id,
            balance=5000,
            currency="JPY",
            goal_name=None,
            goal_amount=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        mock_account_repository.add(child_account)

        # テスト
        service = injector_with_mocks.get(ProfileService)
        result = service.delete_child(sample_profile.id, sample_child.id)

        # 検証
        assert result is True
        assert mock_profile_repository.get_by_id(sample_child.id) is None
        assert len(mock_account_repository.get_by_user_id(sample_child.id)) == 0

    def test_delete_child_not_owned_by_parent(
        self,
        injector_with_mocks: Injector,
        mock_profile_repository: MockProfileRepository,
        mock_family_relationship_repository,
        sample_profile: Profile,
        sample_child: Profile,
    ):
        """他の親の子供を削除しようとした場合をテスト"""
        import uuid

        from app.core.exceptions import InvalidAmountException

        # 準備: 親と子を追加（異なる親）
        sample_profile.role = "parent"
        mock_profile_repository.add(sample_profile)

        sample_child.role = "child"
        mock_profile_repository.add(sample_child)
        # 異なる親と紐付け
        other_parent_id = str(uuid.uuid4())
        mock_family_relationship_repository.add_relationship(other_parent_id, sample_child.id)

        # テスト
        service = injector_with_mocks.get(ProfileService)

        with pytest.raises(InvalidAmountException) as exc_info:
            service.delete_child(sample_profile.id, sample_child.id)

        # 検証
        assert "does not belong to this parent" in exc_info.value.reason

    def test_link_child_to_auth_success(
        self,
        injector_with_mocks: Injector,
        mock_profile_repository: MockProfileRepository,
        sample_child: Profile,
    ):
        """子供プロフィールを認証アカウントにリンクする成功をテスト"""

        # 準備
        sample_child.role = "child"
        sample_child.auth_user_id = None
        mock_profile_repository.add(sample_child)

        auth_id = str(uuid.uuid4())

        # テスト
        service = injector_with_mocks.get(ProfileService)
        linked = service.link_child_to_auth(sample_child.id, auth_id)

        # 検証
        assert linked.auth_user_id == auth_id
        assert linked.id == sample_child.id

    def test_link_child_to_auth_already_linked(
        self,
        injector_with_mocks: Injector,
        mock_profile_repository: MockProfileRepository,
        sample_profile: Profile,
        sample_child: Profile,
    ):
        """既にリンクされている認証アカウントにリンクしようとした場合をテスト"""

        # 準備: 既存のプロフィールに認証アカウントをリンク
        auth_id = str(uuid.uuid4())

        existing = replace(sample_profile, auth_user_id=auth_id)
        mock_profile_repository.add(existing)

        sample_child.role = "child"
        sample_child.auth_user_id = None
        mock_profile_repository.add(sample_child)

        # テスト
        service = injector_with_mocks.get(ProfileService)

        with pytest.raises(InvalidAmountException) as exc_info:
            service.link_child_to_auth(sample_child.id, auth_id)

        # 検証
        assert "already linked" in exc_info.value.reason

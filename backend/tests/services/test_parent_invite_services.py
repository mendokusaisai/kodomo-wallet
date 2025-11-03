"""ProfileService の親招待フローに関するテスト"""

from datetime import UTC, datetime, timedelta

import pytest
from injector import Injector

from app.core.exceptions import InvalidAmountException
from app.domain.entities import Profile
from app.repositories.mock_repositories import (
    MockFamilyRelationshipRepository,
    MockProfileRepository,
)
from app.services import ProfileService


class TestParentInviteService:
    """親招待フローのサービスレイヤーテスト"""

    def test_create_parent_invite_success(
        self,
        injector_with_mocks: Injector,
        mock_profile_repository: MockProfileRepository,
        mock_family_relationship_repository: MockFamilyRelationshipRepository,
    ) -> None:
        """親が招待する正常系: トークンが発行され、招待がDBに保存される"""
        # 準備: 親と子のプロフィールを作成
        parent = Profile(
            id="p1",
            auth_user_id="auth-parent",
            email=None,
            name="Parent",
            role="parent",
            avatar_url=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        child = Profile(
            id="c1",
            auth_user_id=None,
            email=None,
            name="Child",
            role="child",
            avatar_url=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        mock_profile_repository.add(parent)
        mock_profile_repository.add(child)
        mock_family_relationship_repository.add_relationship("p1", "c1")

        service = injector_with_mocks.get(ProfileService)

        # 実行: 子どもIDは不要、招待者の全ての子どもと紐づく
        token = service.create_parent_invite("p1", "invitee@example.com")

        # 検証
        assert isinstance(token, str) and len(token) > 0
        # リポジトリ経由で招待を取得し、基本的な値を検証
        invite = service.parent_invite_repo.get_by_token(token)  # type: ignore[attr-defined]
        assert invite is not None
        assert invite.child_id == "c1"  # 最初の子どもが代表として保存される
        assert invite.inviter_id == "p1"
        assert invite.email == "invitee@example.com"
        assert invite.status == "pending"

    def test_create_parent_invite_no_children(
        self,
        injector_with_mocks: Injector,
        mock_profile_repository: MockProfileRepository,
    ) -> None:
        """子どもがいない場合、招待作成はエラーになる"""
        # 準備: 親はいるが子どもがいない
        parent = Profile(
            id="p1",
            auth_user_id="auth-parent",
            email=None,
            name="Parent",
            role="parent",
            avatar_url=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        mock_profile_repository.add(parent)

        service = injector_with_mocks.get(ProfileService)

        # 実行 & 検証: 子どもがいないためエラーが発生する
        with pytest.raises(InvalidAmountException):
            service.create_parent_invite("p1", "invitee@example.com")

    def test_accept_parent_invite_success(
        self,
        injector_with_mocks: Injector,
        mock_profile_repository: MockProfileRepository,
        mock_family_relationship_repository: MockFamilyRelationshipRepository,
    ) -> None:
        """招待の受理が成功すると、親子関係が作成され、招待はacceptedになる"""
        # 準備
        parent = Profile(
            id="p2",
            auth_user_id="auth-parent2",
            email=None,
            name="Parent2",
            role="parent",
            avatar_url=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        child = Profile(
            id="c2",
            auth_user_id=None,
            email=None,
            name="Child2",
            role="child",
            avatar_url=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        mock_profile_repository.add(parent)
        mock_profile_repository.add(child)

        service = injector_with_mocks.get(ProfileService)
        # 招待を作成するには、招待者が子を持っている必要がある
        # まず p2 と c2 の関係を作って認可を満たす
        mock_family_relationship_repository.add_relationship("p2", "c2")
        token = service.create_parent_invite("p2", "invitee2@example.com")

        # 実行: 受け入れ側の親として p2 自身を想定(例として妥当)
        ok = service.accept_parent_invite(token, "p2")

        # 検証
        assert ok is True
        assert mock_family_relationship_repository.has_relationship("p2", "c2")
        invite = service.parent_invite_repo.get_by_token(token)  # type: ignore[attr-defined]
        assert invite is not None and invite.status == "accepted"

    def test_accept_parent_invite_expired(
        self,
        injector_with_mocks: Injector,
        mock_profile_repository: MockProfileRepository,
        mock_family_relationship_repository: MockFamilyRelationshipRepository,
    ) -> None:
        """期限切れの招待を受理しようとするとエラーになり、招待はexpiredになる"""
        # 準備
        parent = Profile(
            id="p3",
            auth_user_id="auth-parent3",
            email=None,
            name="Parent3",
            role="parent",
            avatar_url=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        child = Profile(
            id="c3",
            auth_user_id=None,
            email=None,
            name="Child3",
            role="child",
            avatar_url=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        mock_profile_repository.add(parent)
        mock_profile_repository.add(child)

        service = injector_with_mocks.get(ProfileService)
        mock_family_relationship_repository.add_relationship("p3", "c3")
        # 招待を作成し、モックを直接書き換えて期限切れにする
        token = service.create_parent_invite("p3", "invitee3@example.com")
        invite = service.parent_invite_repo.get_by_token(token)  # type: ignore[attr-defined]
        assert invite is not None
        # 過去日時を設定して期限切れにする
        past = datetime.now(UTC) - timedelta(days=1)
        # モック内の値を置き換え
        updated = invite.__class__(
            id=invite.id,
            token=invite.token,
            child_id=invite.child_id,
            inviter_id=invite.inviter_id,
            email=invite.email,
            status=invite.status,
            expires_at=past,
            created_at=invite.created_at,
        )
        # 変更を保存
        service.parent_invite_repo.invites[token] = updated  # type: ignore[attr-defined]

        # 実行 & 検証: 期限切れエラーが発生し、ステータスがexpiredになる
        with pytest.raises(InvalidAmountException):
            service.accept_parent_invite(token, "p3")
        after = service.parent_invite_repo.get_by_token(token)  # type: ignore[attr-defined]
        assert after is not None and after.status == "expired"

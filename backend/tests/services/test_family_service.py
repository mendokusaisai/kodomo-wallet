"""FamilyService のユニットテスト"""

import pytest
from injector import Injector

from app.core.exceptions import ResourceNotFoundException
from app.repositories.mock_repositories import (
    MockChildInviteRepository,
    MockFamilyMemberRepository,
    MockFamilyRepository,
    MockParentInviteRepository,
)
from app.services.family_service import FamilyService

from .conftest import CHILD_UID, FAMILY_ID, PARENT_UID


class TestFamilyService:
    """FamilyService のテストスイート"""

    def test_create_family_with_parent_success(
        self,
        injector_with_mocks: Injector,
        mock_family_repository: MockFamilyRepository,
        mock_member_repository: MockFamilyMemberRepository,
    ):
        """新規家族と親メンバーを作成できる"""
        service = injector_with_mocks.get(FamilyService)
        family, member = service.create_family_with_parent(
            uid="new-parent-uid",
            name="田中太郎",
            email="tanaka@example.com",
            family_name="田中家",
        )
        assert family.name == "田中家"
        assert member.uid == "new-parent-uid"
        assert member.role == "parent"
        assert member.family_id == family.id
        stored_family = mock_family_repository.get_by_id(family.id)
        assert stored_family is not None

    def test_invite_child_as_parent_success(
        self,
        injector_with_mocks: Injector,
        mock_child_invite_repository: MockChildInviteRepository,
    ):
        """親が子供を招待できる"""
        service = injector_with_mocks.get(FamilyService)
        invite = service.invite_child(
            family_id=FAMILY_ID,
            inviter_uid=PARENT_UID,
            child_name="太郎",
        )
        assert invite.family_id == FAMILY_ID
        assert invite.child_name == "太郎"
        assert invite.accepted_at is None

    def test_invite_child_as_child_fails(
        self,
        injector_with_mocks: Injector,
    ):
        """子供が招待を送ろうとするとエラー"""
        from app.core.exceptions import InvalidAmountException
        service = injector_with_mocks.get(FamilyService)
        with pytest.raises(InvalidAmountException):
            service.invite_child(
                family_id=FAMILY_ID,
                inviter_uid=CHILD_UID,
                child_name="花子",
            )

    def test_accept_child_invite_success(
        self,
        injector_with_mocks: Injector,
        mock_child_invite_repository: MockChildInviteRepository,
        mock_member_repository: MockFamilyMemberRepository,
    ):
        """子供が招待を受け入れてメンバーになれる"""
        service = injector_with_mocks.get(FamilyService)
        invite = service.invite_child(
            family_id=FAMILY_ID,
            inviter_uid=PARENT_UID,
            child_name="新しい子供",
        )
        member = service.accept_child_invite(
            token=invite.token,
            uid="new-child-uid",
        )
        assert member.uid == "new-child-uid"
        assert member.role == "child"
        assert member.family_id == FAMILY_ID
        updated_invite = mock_child_invite_repository.get_by_token(invite.token)
        assert updated_invite is not None
        assert updated_invite.accepted_at is not None

    def test_accept_child_invite_invalid_token(
        self,
        injector_with_mocks: Injector,
    ):
        """無効なトークンで招待を受け入れるとエラー"""
        service = injector_with_mocks.get(FamilyService)
        with pytest.raises(ResourceNotFoundException):
            service.accept_child_invite(
                token="invalid-token",
                uid="new-child-uid",
            )

    def test_invite_parent_as_parent_success(
        self,
        injector_with_mocks: Injector,
        mock_parent_invite_repository: MockParentInviteRepository,
    ):
        """既存の親が別の親を招待できる"""
        service = injector_with_mocks.get(FamilyService)
        invite = service.invite_parent(
            family_id=FAMILY_ID,
            inviter_uid=PARENT_UID,
            email="new-parent@example.com",
        )
        assert invite.family_id == FAMILY_ID
        assert invite.inviter_uid == PARENT_UID
        assert invite.accepted_at is None

    def test_accept_parent_invite_success(
        self,
        injector_with_mocks: Injector,
        mock_parent_invite_repository: MockParentInviteRepository,
        mock_member_repository: MockFamilyMemberRepository,
    ):
        """招待された親がメンバーになれる"""
        service = injector_with_mocks.get(FamilyService)
        invite = service.invite_parent(
            family_id=FAMILY_ID,
            inviter_uid=PARENT_UID,
            email="new-parent@example.com",
        )
        member = service.accept_parent_invite(
            token=invite.token,
            uid="new-parent-uid",
            name="新しい親",
            email="new-parent@example.com",
        )
        assert member.uid == "new-parent-uid"
        assert member.role == "parent"
        assert member.family_id == FAMILY_ID
        updated_invite = mock_parent_invite_repository.get_by_token(invite.token)
        assert updated_invite is not None
        assert updated_invite.accepted_at is not None

    def test_accept_parent_invite_invalid_token(
        self,
        injector_with_mocks: Injector,
    ):
        """無効なトークンで招待を受け入れるとエラー"""
        service = injector_with_mocks.get(FamilyService)
        with pytest.raises(ResourceNotFoundException):
            service.accept_parent_invite(
                token="invalid-token",
                uid="new-parent-uid",
                name="親",
                email="parent@example.com",
            )

"""FamilyRepository + FamilyMemberRepository の Firestore Emulator テスト"""

from datetime import UTC, datetime

import pytest

from app.repositories.firestore.family_member_repository import FirestoreFamilyMemberRepository
from app.repositories.firestore.family_repository import FirestoreFamilyRepository


@pytest.fixture(autouse=True)
def cleanup_firestore():
    """各テスト後に Firestore Emulator のデータをクリア"""
    from app.core.database import get_firestore_client
    yield
    db = get_firestore_client()
    # テストで使用したドキュメントを削除
    for doc in db.collection("families").stream():
        doc.reference.delete()


class TestFirestoreFamilyRepository:
    def test_create_and_get_family(self):
        repo = FirestoreFamilyRepository()
        family = repo.create(name="テスト家族")
        assert family.id
        assert family.name == "テスト家族"

        fetched = repo.get_by_id(family.id)
        assert fetched is not None
        assert fetched.id == family.id
        assert fetched.name == "テスト家族"

    def test_get_by_id_not_found(self):
        repo = FirestoreFamilyRepository()
        result = repo.get_by_id("non-existent-id")
        assert result is None

    def test_create_family_without_name(self):
        repo = FirestoreFamilyRepository()
        family = repo.create(name=None)
        assert family.id
        assert family.name is None


class TestFirestoreFamilyMemberRepository:
    def test_create_and_get_member(self):
        family_repo = FirestoreFamilyRepository()
        member_repo = FirestoreFamilyMemberRepository()

        family = family_repo.create(name="テスト家族")
        member = member_repo.create(
            family_id=family.id,
            uid="test-uid-001",
            name="田中太郎",
            role="parent",
            email="taro@example.com",
        )
        assert member.uid == "test-uid-001"
        assert member.role == "parent"

        fetched = member_repo.get_by_uid(family.id, "test-uid-001")
        assert fetched is not None
        assert fetched.name == "田中太郎"

    def test_list_members(self):
        family_repo = FirestoreFamilyRepository()
        member_repo = FirestoreFamilyMemberRepository()

        family = family_repo.create(name="テスト家族")
        member_repo.create(family_id=family.id, uid="uid-parent", name="親", role="parent")
        member_repo.create(family_id=family.id, uid="uid-child", name="子供", role="child")

        members = member_repo.list_members(family.id)
        assert len(members) == 2
        roles = {m.role for m in members}
        assert "parent" in roles
        assert "child" in roles

    def test_get_by_uid_not_found(self):
        member_repo = FirestoreFamilyMemberRepository()
        result = member_repo.get_by_uid("any-family", "non-existent-uid")
        assert result is None

    def test_delete_member(self):
        family_repo = FirestoreFamilyRepository()
        member_repo = FirestoreFamilyMemberRepository()

        family = family_repo.create(name="テスト家族")
        member_repo.create(family_id=family.id, uid="uid-to-delete", name="削除対象", role="child")

        deleted = member_repo.delete(family.id, "uid-to-delete")
        assert deleted is True

        result = member_repo.get_by_uid(family.id, "uid-to-delete")
        assert result is None

    def test_delete_member_not_found(self):
        member_repo = FirestoreFamilyMemberRepository()
        result = member_repo.delete("any-family", "non-existent")
        assert result is False

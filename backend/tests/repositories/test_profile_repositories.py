import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.repositories.sqlalchemy import (
    SQLAlchemyProfileRepository,
)
from app.repositories.sqlalchemy.models import Profile


# ============================================================================
# SQLAlchemyProfileRepository Tests
# ============================================================================
class TestSQLAlchemyProfileRepository:
    """SQLAlchemyProfileRepository のテストスイート"""

    def test_get_by_id_returns_none_when_not_found(self, in_memory_db: Session):
        """プロフィールが存在しない場合に get_by_id が None を返すことをテスト"""
        repo = SQLAlchemyProfileRepository(in_memory_db)
        result = repo.get_by_id(str(uuid.uuid4()))
        assert result is None

    def test_add_and_get_profile(self, in_memory_db: Session, sample_profile: Profile):
        """プロフィールを追加して取得できることをテスト"""
        in_memory_db.add(sample_profile)
        in_memory_db.commit()

        repo = SQLAlchemyProfileRepository(in_memory_db)
        result = repo.get_by_id(str(sample_profile.id))

        assert result is not None
        assert result.id == str(sample_profile.id)
        assert str(result.name) == "Test User"
        assert str(result.role) == "parent"

    def test_get_children(self, in_memory_db: Session):
        """親の子プロフィールを全て取得できることをテスト"""
        now = datetime.now(UTC)
        parent = Profile(
            id=uuid.uuid4(),
            name="Parent",
            role="parent",
            avatar_url=None,
            created_at=now,
            updated_at=now,
        )
        child1 = Profile(
            id=uuid.uuid4(),
            name="Child 1",
            role="child",
            avatar_url=None,
            created_at=now,
            updated_at=now,
        )
        child2 = Profile(
            id=uuid.uuid4(),
            name="Child 2",
            role="child",
            avatar_url=None,
            created_at=now,
            updated_at=now,
        )
        in_memory_db.add_all([parent, child1, child2])
        # 親子関係を作成
        from app.repositories.sqlalchemy.models import FamilyRelationship

        in_memory_db.add(
            FamilyRelationship(
                id=uuid.uuid4(),
                parent_id=parent.id,
                child_id=child1.id,
                relationship_type="parent",
                created_at=now,
            )
        )
        in_memory_db.add(
            FamilyRelationship(
                id=uuid.uuid4(),
                parent_id=parent.id,
                child_id=child2.id,
                relationship_type="parent",
                created_at=now,
            )
        )
        in_memory_db.commit()

        repo = SQLAlchemyProfileRepository(in_memory_db)
        children = repo.get_children(str(parent.id))

        assert len(children) == 2
        child_names = {str(c.name) for c in children}
        assert "Child 1" in child_names
        assert "Child 2" in child_names

    def test_get_children_returns_empty_when_no_children(self, in_memory_db: Session):
        """子がいない場合に空のリストを返すことをテスト"""
        now = datetime.now(UTC)
        parent = Profile(
            id=uuid.uuid4(),
            name="Parent",
            role="parent",
            avatar_url=None,
            created_at=now,
            updated_at=now,
        )
        in_memory_db.add(parent)
        in_memory_db.commit()

        repo = SQLAlchemyProfileRepository(in_memory_db)
        children = repo.get_children(str(parent.id))

        assert len(children) == 0

    def test_get_by_auth_user_id(self, in_memory_db: Session):
        """認証ユーザー ID でプロフィールを取得できることをテスト"""
        now = datetime.now(UTC)
        auth_user_id = uuid.uuid4()
        profile = Profile(
            id=auth_user_id,  # 現行スキーマでは profiles.id == auth.users.id
            name="Auth User",
            role="parent",
            avatar_url=None,
            created_at=now,
            updated_at=now,
        )
        in_memory_db.add(profile)
        in_memory_db.commit()

        repo = SQLAlchemyProfileRepository(in_memory_db)
        result = repo.get_by_auth_user_id(str(auth_user_id))

        assert result is not None
        assert str(result.id) == str(auth_user_id)
        assert str(result.name) == "Auth User"

    def test_get_by_auth_user_id_returns_none_when_not_found(self, in_memory_db: Session):
        """存在しない認証ユーザー ID で None を返すことをテスト"""
        repo = SQLAlchemyProfileRepository(in_memory_db)
        result = repo.get_by_auth_user_id(str(uuid.uuid4()))
        assert result is None

    def test_delete(self, in_memory_db: Session):
        """プロフィールを削除できることをテスト"""
        now = datetime.now(UTC)
        profile = Profile(
            id=uuid.uuid4(),
            name="To Delete",
            role="child",
            avatar_url=None,
            created_at=now,
            updated_at=now,
        )
        in_memory_db.add(profile)
        in_memory_db.commit()

        repo = SQLAlchemyProfileRepository(in_memory_db)
        result = repo.delete(str(profile.id))
        in_memory_db.commit()

        assert result is True

        # 削除後は取得できない
        assert repo.get_by_id(str(profile.id)) is None

    def test_delete_returns_false_when_not_found(self, in_memory_db: Session):
        """存在しないプロフィールの削除で False を返すことをテスト"""
        repo = SQLAlchemyProfileRepository(in_memory_db)
        result = repo.delete(str(uuid.uuid4()))
        assert result is False

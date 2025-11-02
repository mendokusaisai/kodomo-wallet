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
        parent = Profile(
            id=uuid.uuid4(),
            name="Parent",
            email="parent@example.com",
            role="parent",
            parent_id=None,
            auth_user_id=None,
            avatar_url=None,
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        child1 = Profile(
            id=uuid.uuid4(),
            name="Child 1",
            email=None,
            role="child",
            parent_id=parent.id,
            auth_user_id=None,
            avatar_url=None,
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        child2 = Profile(
            id=uuid.uuid4(),
            name="Child 2",
            email=None,
            role="child",
            parent_id=parent.id,
            auth_user_id=None,
            avatar_url=None,
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add_all([parent, child1, child2])
        in_memory_db.commit()

        repo = SQLAlchemyProfileRepository(in_memory_db)
        children = repo.get_children(str(parent.id))

        assert len(children) == 2
        child_names = {str(c.name) for c in children}
        assert "Child 1" in child_names
        assert "Child 2" in child_names

    def test_get_children_returns_empty_when_no_children(self, in_memory_db: Session):
        """子がいない場合に空のリストを返すことをテスト"""
        parent = Profile(
            id=uuid.uuid4(),
            name="Parent",
            email="parent@example.com",
            role="parent",
            parent_id=None,
            auth_user_id=None,
            avatar_url=None,
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add(parent)
        in_memory_db.commit()

        repo = SQLAlchemyProfileRepository(in_memory_db)
        children = repo.get_children(str(parent.id))

        assert len(children) == 0

    def test_get_by_auth_user_id(self, in_memory_db: Session):
        """認証ユーザー ID でプロフィールを取得できることをテスト"""
        auth_user_id = uuid.uuid4()
        profile = Profile(
            id=uuid.uuid4(),
            name="Auth User",
            email="auth@example.com",
            role="parent",
            parent_id=None,
            auth_user_id=auth_user_id,
            avatar_url=None,
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add(profile)
        in_memory_db.commit()

        repo = SQLAlchemyProfileRepository(in_memory_db)
        result = repo.get_by_auth_user_id(str(auth_user_id))

        assert result is not None
        assert str(result.auth_user_id) == str(auth_user_id)
        assert str(result.name) == "Auth User"

    def test_get_by_auth_user_id_returns_none_when_not_found(self, in_memory_db: Session):
        """存在しない認証ユーザー ID で None を返すことをテスト"""
        repo = SQLAlchemyProfileRepository(in_memory_db)
        result = repo.get_by_auth_user_id(str(uuid.uuid4()))
        assert result is None

    def test_get_by_email(self, in_memory_db: Session):
        """メールアドレスで未認証プロフィールを取得できることをテスト"""
        profile = Profile(
            id=uuid.uuid4(),
            name="Invited Child",
            email="child@example.com",
            role="child",
            parent_id=uuid.uuid4(),
            auth_user_id=None,  # 未認証
            avatar_url=None,
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add(profile)
        in_memory_db.commit()

        repo = SQLAlchemyProfileRepository(in_memory_db)
        result = repo.get_by_email("child@example.com")

        assert result is not None
        assert str(result.email) == "child@example.com"
        assert result.auth_user_id is None

    def test_get_by_email_returns_none_when_not_found(self, in_memory_db: Session):
        """存在しないメールアドレスで None を返すことをテスト"""
        repo = SQLAlchemyProfileRepository(in_memory_db)
        result = repo.get_by_email("nonexistent@example.com")
        assert result is None

    def test_get_by_email_ignores_authenticated_profiles(self, in_memory_db: Session):
        """認証済みプロフィールは取得しないことをテスト"""
        profile = Profile(
            id=uuid.uuid4(),
            name="Auth User",
            email="auth@example.com",
            role="parent",
            parent_id=None,
            auth_user_id=uuid.uuid4(),  # 認証済み
            avatar_url=None,
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add(profile)
        in_memory_db.commit()

        repo = SQLAlchemyProfileRepository(in_memory_db)
        result = repo.get_by_email("auth@example.com")

        assert result is None  # 認証済みなので取得されない

    def test_create_child(self, in_memory_db: Session):
        """子プロフィールを作成できることをテスト"""
        parent = Profile(
            id=uuid.uuid4(),
            name="Parent",
            email="parent@example.com",
            role="parent",
            parent_id=None,
            auth_user_id=None,
            avatar_url=None,
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add(parent)
        in_memory_db.commit()

        repo = SQLAlchemyProfileRepository(in_memory_db)
        child = repo.create_child(
            name="New Child", parent_id=str(parent.id), email="child@example.com"
        )
        in_memory_db.commit()

        assert child.id is not None
        assert str(child.name) == "New Child"
        assert str(child.parent_id) == str(parent.id)
        assert str(child.email) == "child@example.com"
        assert str(child.role) == "child"
        assert child.auth_user_id is None

    def test_create_child_without_email(self, in_memory_db: Session):
        """メールアドレスなしで子プロフィールを作成できることをテスト"""
        parent = Profile(
            id=uuid.uuid4(),
            name="Parent",
            email="parent@example.com",
            role="parent",
            parent_id=None,
            auth_user_id=None,
            avatar_url=None,
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add(parent)
        in_memory_db.commit()

        repo = SQLAlchemyProfileRepository(in_memory_db)
        child = repo.create_child(name="New Child", parent_id=str(parent.id), email=None)
        in_memory_db.commit()

        assert child.id is not None
        assert str(child.name) == "New Child"
        assert child.email is None

    def test_link_to_auth(self, in_memory_db: Session):
        """既存プロフィールを認証アカウントに紐付けできることをテスト"""
        profile = Profile(
            id=uuid.uuid4(),
            name="Child",
            email="child@example.com",
            role="child",
            parent_id=uuid.uuid4(),
            auth_user_id=None,
            avatar_url=None,
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        in_memory_db.add(profile)
        in_memory_db.commit()

        auth_user_id = str(uuid.uuid4())
        repo = SQLAlchemyProfileRepository(in_memory_db)
        updated_profile = repo.link_to_auth(str(profile.id), auth_user_id)
        in_memory_db.commit()

        assert str(updated_profile.auth_user_id) == auth_user_id
        assert str(updated_profile.id) == str(profile.id)

        # DB から再取得して確認
        result = repo.get_by_id(str(profile.id))
        assert result is not None
        assert str(result.auth_user_id) == auth_user_id

    def test_delete(self, in_memory_db: Session):
        """プロフィールを削除できることをテスト"""
        profile = Profile(
            id=uuid.uuid4(),
            name="To Delete",
            email="delete@example.com",
            role="child",
            parent_id=uuid.uuid4(),
            auth_user_id=None,
            avatar_url=None,
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
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

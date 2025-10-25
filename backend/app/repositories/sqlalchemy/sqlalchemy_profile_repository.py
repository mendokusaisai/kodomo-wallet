import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.models import Profile
from app.repositories.interfaces import (
    ProfileRepository,
)


class SQLAlchemyProfileRepository(ProfileRepository):
    """ProfileRepositoryのSQLAlchemy実装"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: str) -> Profile | None:
        """IDでプロフィールを取得"""
        return self.db.query(Profile).filter(Profile.id == uuid.UUID(user_id)).first()

    def get_children(self, parent_id: str) -> list[Profile]:
        """親の全ての子プロフィールを取得"""
        return list(self.db.query(Profile).filter(Profile.parent_id == uuid.UUID(parent_id)).all())

    def get_by_auth_user_id(self, auth_user_id: str) -> Profile | None:
        """認証ユーザーIDでプロフィールを取得"""
        return (
            self.db.query(Profile).filter(Profile.auth_user_id == uuid.UUID(auth_user_id)).first()
        )

    def get_by_email(self, email: str) -> Profile | None:
        """メールアドレスで未認証プロフィールを取得（auth_user_idがNULL）"""
        return (
            self.db.query(Profile)
            .filter(Profile.email == email)
            .filter(Profile.auth_user_id.is_(None))  # 未認証のみ
            .first()
        )

    def create_child(self, name: str, parent_id: str, email: str | None = None) -> Profile:
        """認証なしで子プロフィールを作成"""
        from datetime import UTC

        profile = Profile(
            id=uuid.uuid4(),
            auth_user_id=None,  # 認証なし
            email=email,  # メールアドレス（任意）
            name=name,
            role="child",
            parent_id=uuid.UUID(parent_id),
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        self.db.add(profile)
        self.db.flush()
        return profile

    def link_to_auth(self, profile_id: str, auth_user_id: str) -> Profile:
        """既存プロフィールを認証アカウントに紐付け"""
        from datetime import UTC

        profile = self.get_by_id(profile_id)
        if not profile:
            raise ValueError(f"Profile {profile_id} not found")

        # 既に認証アカウントが紐づいている場合はエラー
        elif profile.auth_user_id:
            raise ValueError(f"Profile {profile_id} already linked to auth account")

        profile.auth_user_id = uuid.UUID(auth_user_id)
        profile.updated_at = str(datetime.now(UTC))
        self.db.flush()
        return profile

    def delete(self, user_id: str) -> bool:
        """プロフィールを削除"""
        profile = self.get_by_id(user_id)
        if not profile:
            return False
        self.db.delete(profile)
        self.db.flush()
        return True

import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.domain.entities import Profile
from app.repositories.interfaces import ProfileRepository
from app.repositories.sqlalchemy import models as db_models
from app.repositories.sqlalchemy.mapper import to_domain_profile


class SQLAlchemyProfileRepository(ProfileRepository):
    """ProfileRepositoryのSQLAlchemy実装"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: str) -> Profile | None:
        """IDでプロフィールを取得"""
        db_profile = (
            self.db.query(db_models.Profile)
            .filter(db_models.Profile.id == uuid.UUID(user_id))
            .first()
        )
        return to_domain_profile(db_profile) if db_profile else None

    def get_children(self, parent_id: str) -> list[Profile]:
        """親の全ての子プロフィールを取得"""
        db_profiles = (
            self.db.query(db_models.Profile)
            .join(
                db_models.FamilyRelationship,
                db_models.Profile.id == db_models.FamilyRelationship.child_id,
            )
            .filter(db_models.FamilyRelationship.parent_id == uuid.UUID(parent_id))
            .all()
        )
        return [to_domain_profile(p) for p in db_profiles]

    def get_by_auth_user_id(self, auth_user_id: str) -> Profile | None:
        """認証ユーザーIDでプロフィールを取得"""
        db_profile = (
            self.db.query(db_models.Profile)
            .filter(db_models.Profile.auth_user_id == uuid.UUID(auth_user_id))
            .first()
        )
        return to_domain_profile(db_profile) if db_profile else None

    def get_by_email(self, email: str) -> Profile | None:
        """メールアドレスで未認証プロフィールを取得（auth_user_idがNULL）"""
        db_profile = (
            self.db.query(db_models.Profile)
            .filter(db_models.Profile.email == email)
            .filter(db_models.Profile.auth_user_id.is_(None))  # 未認証のみ
            .first()
        )
        return to_domain_profile(db_profile) if db_profile else None

    def create_child(self, name: str, parent_id: str, email: str | None = None) -> Profile:
        """認証なしで子プロフィールを作成"""
        from datetime import UTC

        db_profile = db_models.Profile(
            id=uuid.uuid4(),
            auth_user_id=None,  # 認証なし
            email=email,  # メールアドレス（任意）
            name=name,
            role="child",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        self.db.add(db_profile)
        self.db.flush()
        # 親子関係を作成
        relationship = db_models.FamilyRelationship(
            parent_id=uuid.UUID(parent_id),
            child_id=db_profile.id,
            relationship_type="parent",
            created_at=str(datetime.now(UTC)),
        )
        self.db.add(relationship)
        self.db.flush()
        self.db.refresh(db_profile)
        return to_domain_profile(db_profile)

    def link_to_auth(self, profile_id: str, auth_user_id: str) -> Profile:
        """既存プロフィールを認証アカウントに紐付け"""
        from datetime import UTC

        db_profile = (
            self.db.query(db_models.Profile)
            .filter(db_models.Profile.id == uuid.UUID(profile_id))
            .first()
        )

        if not db_profile:
            raise ValueError(f"Profile {profile_id} not found")

        # 既に認証アカウントが紐づいている場合はエラー
        if db_profile.auth_user_id is not None:  # type: ignore
            raise ValueError(f"Profile {profile_id} already linked to auth account")

        db_profile.auth_user_id = uuid.UUID(auth_user_id)  # type: ignore
        db_profile.updated_at = str(datetime.now(UTC))  # type: ignore
        self.db.flush()
        self.db.refresh(db_profile)
        return to_domain_profile(db_profile)

    def delete(self, user_id: str) -> bool:
        """プロフィールを削除"""
        db_profile = (
            self.db.query(db_models.Profile)
            .filter(db_models.Profile.id == uuid.UUID(user_id))
            .first()
        )
        if not db_profile:
            return False
        self.db.delete(db_profile)
        self.db.flush()
        return True

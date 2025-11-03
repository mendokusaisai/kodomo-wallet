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
        """認証ユーザーIDでプロフィールを取得
        スキーマ変更により profiles.id と auth.users.id は同一のため、id 検索にフォールバック
        """
        db_profile = (
            self.db.query(db_models.Profile)
            .filter(db_models.Profile.id == uuid.UUID(auth_user_id))
            .first()
        )
        return to_domain_profile(db_profile) if db_profile else None

    def get_by_email(self, email: str) -> Profile | None:
        """メールアドレスで未認証プロフィールを取得
        現行スキーマでは profiles に email を保持しないため、常に None を返す
        """
        return None

    def create_child(self, name: str, parent_id: str, email: str | None = None) -> Profile:
        """
        認証なしで子プロフィールを作成
        作成した親および関連する全親との関係を自動作成
        """
        from datetime import UTC

        db_profile = db_models.Profile(
            id=uuid.uuid4(),
            auth_user_id=None,  # 認証なし
            email=email,  # メールアドレス(任意)
            name=name,
            role="child",
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        self.db.add(db_profile)
        self.db.flush()

        # 作成した親との関係を作成
        self._create_family_relationship(parent_id, str(db_profile.id))

        # 同じ家族の他の親との関係も作成
        related_parents = self._get_related_parents(parent_id)
        for other_parent_id in related_parents:
            self._create_family_relationship(other_parent_id, str(db_profile.id))

        self.db.refresh(db_profile)
        return to_domain_profile(db_profile)

    def _get_related_parents(self, parent_id: str) -> list[str]:
        """指定した親と同じ子を持つ他の親を取得"""
        children = (
            self.db.query(db_models.FamilyRelationship.child_id)
            .filter(db_models.FamilyRelationship.parent_id == uuid.UUID(parent_id))
            .all()
        )

        if not children:
            return []

        child_ids = [c.child_id for c in children]

        other_parents = (
            self.db.query(db_models.FamilyRelationship.parent_id)
            .filter(db_models.FamilyRelationship.child_id.in_(child_ids))
            .filter(db_models.FamilyRelationship.parent_id != uuid.UUID(parent_id))
            .distinct()
            .all()
        )

        return [str(p.parent_id) for p in other_parents]

    def _create_family_relationship(self, parent_id: str, child_id: str) -> None:
        """親子関係を作成(重複は無視)"""
        from datetime import UTC

        from sqlalchemy.exc import IntegrityError

        relationship = db_models.FamilyRelationship(
            parent_id=uuid.UUID(parent_id),
            child_id=uuid.UUID(child_id),
            relationship_type="parent",
            created_at=str(datetime.now(UTC)),
        )
        self.db.add(relationship)

        try:
            self.db.flush()
        except IntegrityError:
            # UNIQUE制約違反 = 既に関係が存在 → 無視
            self.db.rollback()

    def link_to_auth(self, profile_id: str, auth_user_id: str) -> Profile:
        """既存プロフィールを認証アカウントに紐付け
        現行スキーマでは profiles に認証IDを保持しないため、この操作は不要。
        プロフィールをそのまま返す。
        """
        db_profile = (
            self.db.query(db_models.Profile)
            .filter(db_models.Profile.id == uuid.UUID(profile_id))
            .first()
        )
        if not db_profile:
            raise ValueError(f"Profile {profile_id} not found")
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

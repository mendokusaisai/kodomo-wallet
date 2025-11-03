import os
import secrets
import uuid

from sqlalchemy import update
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

    def create_child(self, name: str, parent_id: str, email: str | None = None) -> Profile:
        """子プロフィールを作成
        現行スキーマでは profiles.id は auth.users.id のFKのため、
        auth.users を先に作成し、トリガーで profiles が自動作成される流れを使用します。
        """
        import httpx

        supabase_url = os.getenv("SUPABASE_URL")
        supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if not supabase_url or not supabase_service_key:
            raise ValueError("Supabase configuration not found")

        # 一時的なメールアドレスとパスワードを生成
        if not email:
            # ランダムなメールアドレスを生成
            email = f"child_{secrets.token_hex(8)}@temp.kodomo-wallet.local"

        temp_password = secrets.token_urlsafe(32)

        # Supabase Admin APIで認証ユーザーを作成
        headers = {
            "apikey": supabase_service_key,
            "Authorization": f"Bearer {supabase_service_key}",
            "Content-Type": "application/json",
        }

        # 認証ユーザー作成
        response = httpx.post(
            f"{supabase_url}/auth/v1/admin/users",
            json={
                "email": email,
                "password": temp_password,
                "email_confirm": True,
                "user_metadata": {"role": "child", "name": name},
            },
            headers=headers,
            timeout=30.0,
        )

        if response.status_code != 200:
            raise ValueError(f"Failed to create auth user: {response.text}")

        auth_user = response.json()
        auth_user_id = auth_user["id"]

        # トリガーで自動作成された profiles レコードを取得
        self.db.flush()  # 保留中の変更をコミット
        db_profile = (
            self.db.query(db_models.Profile)
            .filter(db_models.Profile.id == uuid.UUID(auth_user_id))
            .first()
        )

        if not db_profile:
            raise ValueError(f"Profile not created by trigger for auth_user_id: {auth_user_id}")

        # 名前を更新（UPDATE文を使用）
        self.db.execute(
            update(db_models.Profile).where(db_models.Profile.id == db_profile.id).values(name=name)
        )
        self.db.flush()

        # 親子関係を作成
        from datetime import UTC, datetime

        from sqlalchemy.exc import IntegrityError

        relationship = db_models.FamilyRelationship(
            parent_id=uuid.UUID(parent_id),
            child_id=uuid.UUID(auth_user_id),
            relationship_type="parent",
            created_at=datetime.now(UTC),
        )
        self.db.add(relationship)

        try:
            self.db.flush()
        except IntegrityError as exc:
            # UNIQUE制約違反の場合はロールバック
            self.db.rollback()
            raise ValueError(
                f"Family relationship already exists between {parent_id} and {auth_user_id}"
            ) from exc

        return to_domain_profile(db_profile)

    def link_to_auth(self, profile_id: str, auth_user_id: str) -> Profile:
        """既存プロフィールを認証アカウントに紐付け
        現行スキーマでは profiles.id = auth.users.id のFKなので、
        プロフィールIDと認証IDが一致していることを確認するだけです。
        """
        db_profile = (
            self.db.query(db_models.Profile)
            .filter(db_models.Profile.id == uuid.UUID(profile_id))
            .first()
        )

        if not db_profile:
            raise ValueError(f"Profile {profile_id} not found")

        # 現行スキーマでは profiles.id == auth.users.id なので、
        # profile_id と auth_user_id が一致していることを確認
        if str(db_profile.id) != auth_user_id:
            raise ValueError(
                f"Profile ID {profile_id} does not match auth_user_id {auth_user_id}. "
                "In the current schema, profiles.id must equal auth.users.id."
            )

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

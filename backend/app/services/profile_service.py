from dataclasses import replace
from datetime import UTC, datetime

from injector import inject

from app.core.exceptions import InvalidAmountException, ResourceNotFoundException
from app.domain.entities import Profile
from app.repositories.interfaces import (
    AccountRepository,
    FamilyRelationshipRepository,
    ProfileRepository,
)


class ProfileService:
    """プロフィール関連のビジネスロジックサービス"""

    @inject
    def __init__(
        self,
        profile_repo: ProfileRepository,
        account_repo: AccountRepository,
        family_relationship_repo: FamilyRelationshipRepository,
    ):
        self.profile_repo = profile_repo
        self.account_repo = account_repo
        self.family_relationship_repo = family_relationship_repo

    def get_profile(self, user_id: str) -> Profile | None:
        """IDでユーザープロフィールを取得"""
        return self.profile_repo.get_by_id(user_id)

    def get_children(self, parent_id: str) -> list[Profile]:
        """親の全ての子供を取得"""
        return self.profile_repo.get_children(parent_id)

    def get_by_auth_user_id(self, auth_user_id: str) -> Profile | None:
        """認証ユーザーIDでプロフィールを取得"""
        return self.profile_repo.get_by_auth_user_id(auth_user_id)

    def update_profile(
        self,
        user_id: str,
        current_user_id: str,
        name: str | None = None,
        avatar_url: str | None = None,
    ) -> Profile:
        """ユーザープロフィールを更新（自分自身または親が子供を編集可能）"""
        # 対象プロフィールを取得
        profile = self.profile_repo.get_by_id(user_id)
        if not profile:
            raise ResourceNotFoundException("Profile", user_id)

        # 現在のユーザープロフィールを取得
        current_user = self.profile_repo.get_by_id(current_user_id)
        if not current_user:
            raise ResourceNotFoundException("Current user", current_user_id)

        # 権限を確認：ユーザーは自分自身を編集可能、または親が子供を編集可能
        if user_id != current_user_id:
            # 親のみが他のプロフィールを編集可能
            if current_user.role != "parent":
                raise InvalidAmountException(0, "You don't have permission to edit this profile")

            # 親は自分の子供のみを編集可能
            if profile.role != "child" or not self.family_relationship_repo.has_relationship(
                current_user_id, user_id
            ):
                raise InvalidAmountException(0, "You can only edit profiles of your own children")

        # ドメインエンティティを更新（dataclassとして扱う）
        updates: dict = {"updated_at": datetime.now(UTC)}
        if name is not None:
            updates["name"] = name
        if avatar_url is not None:
            updates["avatar_url"] = avatar_url

        updated_profile = replace(profile, **updates)

        # Repositoryに更新メソッドを追加する必要があるが、
        # 今は簡略化のため更新されたエンティティを返す
        # TODO: ProfileRepositoryにupdateメソッドを追加
        return updated_profile

    def create_child(
        self, parent_id: str, child_name: str, initial_balance: int = 0, email: str | None = None
    ) -> Profile:
        """認証なしで子供プロフィールとそのアカウントを作成"""
        # 親が存在するか確認
        parent = self.profile_repo.get_by_id(parent_id)
        if not parent or parent.role != "parent":
            raise ResourceNotFoundException("Parent", parent_id)

        # 子どもプロフィール作成
        child_profile = self.profile_repo.create_child(child_name, parent_id, email)

        # 子どものアカウント作成
        self.account_repo.create(user_id=child_profile.id, balance=initial_balance, currency="JPY")

        return child_profile

    def delete_child(self, parent_id: str, child_id: str) -> bool:
        """子供プロフィールと関連する全データを削除"""
        # 親が存在するか確認
        parent = self.profile_repo.get_by_id(parent_id)
        if not parent or parent.role != "parent":
            raise ResourceNotFoundException("Parent", parent_id)

        # 子どもが存在するか確認
        child = self.profile_repo.get_by_id(child_id)
        if not child or child.role != "child":
            raise ResourceNotFoundException("Child", child_id)

        # 子どもが実際にこの親のものか確認
        if not self.family_relationship_repo.has_relationship(parent_id, child_id):
            raise InvalidAmountException(0, "Child does not belong to this parent")

        # 子どもに紐づくアカウントを取得
        accounts = self.account_repo.get_by_user_id(child_id)

        # アカウントを削除（トランザクション、出金リクエストもカスケード削除される）
        for account in accounts:
            self.account_repo.delete(account.id)

        # プロフィールを削除
        self.profile_repo.delete(child_id)

        return True

    def link_child_to_auth(self, child_id: str, auth_user_id: str) -> Profile:
        """子供プロフィールを認証アカウントにリンク"""
        # 子どもプロフィールが存在するか確認
        child = self.profile_repo.get_by_id(child_id)
        if not child or child.role != "child":
            raise ResourceNotFoundException("Child", child_id)

        # 認証アカウントに既に紐づいているプロフィールがないか確認
        existing_profile = self.profile_repo.get_by_auth_user_id(auth_user_id)
        if existing_profile:
            raise InvalidAmountException(
                0, f"Auth account already linked to profile {existing_profile.id}"
            )

        return self.profile_repo.link_to_auth(child_id, auth_user_id)

    def link_child_to_auth_by_email(self, child_id: str, email: str) -> Profile:
        """メールアドレスで子供プロフィールを認証アカウントにリンク"""
        # Supabase auth.users テーブルからメールアドレスで認証アカウントを検索
        # 注意: この実装はSupabaseの直接アクセスが必要
        # 簡略化のため、auth_user_idを取得する処理を追加
        from sqlalchemy import text

        from app.core.database import get_db

        db = next(get_db())

        # auth.users からメールアドレスで検索
        result = db.execute(
            text("SELECT id FROM auth.users WHERE email = :email"), {"email": email}
        ).fetchone()

        if not result:
            raise ResourceNotFoundException("Auth user", email)

        auth_user_id = str(result[0])
        return self.link_child_to_auth(child_id, auth_user_id)

    def auto_link_on_signup(self, auth_user_id: str, email: str) -> Profile | None:
        """サインアップ時にメールアドレスが一致する場合、未認証子供プロフィールを自動的にリンク"""
        # メールアドレスで未認証子どもプロフィールを検索
        child_profile = self.profile_repo.get_by_email(email)

        if child_profile:
            # 自動的に紐付け
            return self.profile_repo.link_to_auth(str(child_profile.id), auth_user_id)

        return None

    def invite_child_to_auth(self, child_id: str, email: str) -> Profile:
        """子供を認証アカウント作成に招待しプロフィールをリンク"""
        import os

        import httpx

        supabase_url = os.getenv("SUPABASE_URL")
        supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if not supabase_url or not supabase_service_key:
            raise ValueError("Supabase configuration not found")

        # 子どもプロフィールが存在するか確認
        child = self.profile_repo.get_by_id(child_id)
        if not child or child.role != "child":
            raise ResourceNotFoundException("Child", child_id)

        # プロフィールにメールアドレスを保存（dataclassとして扱う）
        from dataclasses import replace

        updated_child = replace(child, email=email, updated_at=datetime.now(UTC))
        # TODO: ProfileRepositoryにupdateメソッドを追加して永続化

        # Supabase Management APIで招待メール送信（httpx使用）
        try:
            response = httpx.post(
                f"{supabase_url}/auth/v1/invite",
                headers={
                    "apikey": supabase_service_key,
                    "Authorization": f"Bearer {supabase_service_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "email": email,
                    "data": {
                        "child_profile_id": child_id,
                        "name": updated_child.name,
                        "role": "child",  # 招待経由は必ず子どもロール
                    },
                },
                timeout=10.0,
            )
            response.raise_for_status()
            return child
        except httpx.HTTPError as e:
            raise InvalidAmountException(0, f"Failed to send invitation: {str(e)}") from e

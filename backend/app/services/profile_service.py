from dataclasses import replace
from datetime import UTC, datetime, timedelta

from injector import inject
from sqlalchemy import text

from app.core.config import settings
from app.core.exceptions import InvalidAmountException, ResourceNotFoundException
from app.domain.entities import Profile
from app.repositories.interfaces import (
    AccountRepository,
    ChildInviteRepository,
    FamilyRelationshipRepository,
    ParentInviteRepository,
    ProfileRepository,
)
from app.services.mailer import Mailer


class ProfileService:
    """プロフィール関連のビジネスロジックサービス"""

    @inject
    def __init__(
        self,
        profile_repo: ProfileRepository,
        account_repo: AccountRepository,
        family_relationship_repo: FamilyRelationshipRepository,
        parent_invite_repo: ParentInviteRepository,
        child_invite_repo: ChildInviteRepository,
        mailer: Mailer,
    ):
        self.profile_repo = profile_repo
        self.account_repo = account_repo
        self.family_relationship_repo = family_relationship_repo
        self.parent_invite_repo = parent_invite_repo
        self.child_invite_repo = child_invite_repo
        self.mailer = mailer

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

        # Repositoryを使用してDBに保存
        return self.profile_repo.update(updated_profile)

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

    def invite_child_to_auth(self, child_id: str, email: str) -> str:
        """子供を認証アカウント作成に招待し、招待トークンを返す"""
        from uuid import uuid4

        # 子どもプロフィールが存在するか確認
        child = self.profile_repo.get_by_id(child_id)
        if not child or child.role != "child":
            raise ResourceNotFoundException("Child", child_id)

        # 既に認証アカウントがリンク済みの場合はエラー
        if child.auth_user_id:
            raise InvalidAmountException(0, "Child already has an authentication account")

        # 招待トークンを生成（7日間有効）
        token = str(uuid4())
        expires_at = datetime.now(UTC) + timedelta(days=7)

        # child_invite テーブルに保存
        invite = self.child_invite_repo.create(child_id, email, token, expires_at)

        print(
            f"[DEBUG] Created child invite: token={invite.token}, child_id={child_id}, email={email}, expires_at={expires_at}"
        )

        return invite.token

    def accept_child_invite(self, token: str, auth_user_id: str) -> bool:
        """
        子どもの招待を受け入れる

        新しいフロー:
        1. Google認証後、handle_new_userトリガーで新しいプロフィールが作成される（profiles.id = auth_user_id）
        2. この関数で、既存の子どもプロフィール（親が作成）のデータを新しいプロフィールに移行
        3. 親子関係を更新
        """
        from app.core.database import get_db

        # child_invite テーブルからトークンを検索
        invite = self.child_invite_repo.get_by_token(token)
        if not invite:
            raise ResourceNotFoundException("ChildInvite", f"Token '{token}' not found")

        if invite.status != "pending":
            raise InvalidAmountException(
                0, f"Invitation is {invite.status}. Only pending invitations can be accepted."
            )

        # 期限チェック
        now = datetime.now(UTC)
        if invite.expires_at < now:
            self.child_invite_repo.update_status(invite, "expired")
            raise InvalidAmountException(0, "Invitation expired")

        # 招待されたメールアドレスと認証ユーザーのメールアドレスが一致するかチェック
        auth_user_profile = self.profile_repo.get_by_auth_user_id(auth_user_id)
        if not auth_user_profile:
            raise ResourceNotFoundException("AuthUser", auth_user_id)

        # メールアドレスの検証（大文字小文字を無視）
        if (
            auth_user_profile.email
            and invite.email
            and auth_user_profile.email.lower() != invite.email.lower()
        ):
            raise InvalidAmountException(
                0,
                f"認証アカウントのメールアドレス ({auth_user_profile.email}) が招待されたメールアドレス ({invite.email}) と一致しません",
            )

        # 既存の子どもプロフィールを取得
        old_child_profile = self.profile_repo.get_by_id(invite.child_id)
        if not old_child_profile:
            raise ResourceNotFoundException("Child", invite.child_id)

        # データ移行: 既存の子どもプロフィール → 認証済みプロフィール
        db = next(get_db())
        try:
            # 1. アカウントのuser_idを更新
            db.execute(
                text("UPDATE accounts SET user_id = :new_id WHERE user_id = :old_id"),
                {"new_id": auth_user_id, "old_id": invite.child_id},
            )

            # 2. 親子関係のchild_idを更新
            db.execute(
                text("UPDATE family_relationships SET child_id = :new_id WHERE child_id = :old_id"),
                {"new_id": auth_user_id, "old_id": invite.child_id},
            )

            # 3. 新しいプロフィールに子どもの名前とauth_user_idを更新
            db.execute(
                text(
                    "UPDATE profiles SET name = :name, role = 'child', auth_user_id = :auth_user_id WHERE id = :id"
                ),
                {"name": old_child_profile.name, "auth_user_id": auth_user_id, "id": auth_user_id},
            )

            # 4. 古い子どもプロフィールを削除
            db.execute(text("DELETE FROM profiles WHERE id = :id"), {"id": invite.child_id})

            db.commit()

        except Exception as e:
            db.rollback()
            raise InvalidAmountException(0, f"データ移行に失敗しました: {str(e)}") from e

        # ステータスを更新
        self.child_invite_repo.update_status(invite, "accepted")

        print(
            f"[DEBUG] Accepted child invite: token={token}, auth_user_id={auth_user_id}, migrated from {invite.child_id}"
        )

        return True

    # ===== 親招待（メール/リンク） =====
    def create_parent_invite(self, inviter_id: str, email: str) -> str:
        """
        親を招待する（トークンを発行して返す）
        招待者の全ての子どもと受理者が紐づけられる
        """
        # 認可: inviter が親であること
        inviter = self.profile_repo.get_by_id(inviter_id)
        if not inviter or inviter.role != "parent":
            raise ResourceNotFoundException("Parent", inviter_id)

        # 招待者が少なくとも1人の子どもを持っているか確認
        children = self.profile_repo.get_children(inviter_id)
        if not children:
            raise InvalidAmountException(
                0, "You must have at least one child to invite another parent"
            )

        # 最初の子どもを代表として招待レコードに保存
        # (実際の紐付けは受理時に全ての子どもと行われる)
        representative_child_id = children[0].id

        expires_at = datetime.now(UTC) + timedelta(days=7)
        invite = self.parent_invite_repo.create(
            representative_child_id, inviter_id, email, expires_at
        )

        # デバッグ用ログ
        print(
            f"[DEBUG] Created parent invite: token={invite.token}, child_id={representative_child_id}, inviter_id={inviter_id}, email={email}"
        )

        # 受け入れリンクを作成してスタブメール送信
        accept_link = f"{settings.FRONTEND_ORIGIN}/accept-invite?token={invite.token}"

        # メール本文用に子どもの名前をリスト化
        children_names = ", ".join([child.name for child in children])

        self.mailer.send_parent_invite(
            email,
            accept_link,
            inviter_name=inviter.name,
            child_name=children_names,
        )
        return invite.token

    def accept_parent_invite(self, token: str, current_parent_id: str) -> bool:
        """
        親が招待リンクを受け入れ、親子関係を追加
        招待者の全既存子どもとの関係も自動作成
        """
        invite = self.parent_invite_repo.get_by_token(token)
        if not invite:
            # デバッグ用: トークンが見つからない場合の詳細情報
            raise ResourceNotFoundException(
                "ParentInvite",
                f"Token '{token}' not found in database. "
                f"Please verify the invite link is correct and the invitation exists.",
            )
        if invite.status != "pending":
            raise InvalidAmountException(
                0,
                f"Invitation is {invite.status}. Only pending invitations can be accepted.",
            )

        # 期限チェック
        now = datetime.now(UTC)
        if invite.expires_at < now:
            self.parent_invite_repo.update_status(invite, "expired")
            raise InvalidAmountException(0, "Invitation expired")

        # 受け入れる親が有効か
        parent = self.profile_repo.get_by_id(current_parent_id)
        if not parent or parent.role != "parent":
            raise ResourceNotFoundException("Parent", current_parent_id)

        # 招待された子どもとの関係を作成
        if not self.family_relationship_repo.has_relationship(current_parent_id, invite.child_id):
            self.family_relationship_repo.add_relationship(current_parent_id, invite.child_id)

        # 招待者の全子どもを取得
        inviter_children = self.profile_repo.get_children(invite.inviter_id)

        # 招待された子ども以外の全子どもとの関係も作成
        for child in inviter_children:
            if child.id != invite.child_id:
                self.family_relationship_repo.create_relationship(
                    parent_id=current_parent_id, child_id=child.id
                )

        self.parent_invite_repo.update_status(invite, "accepted")
        return True

    def get_parent_invite_email(self, token: str) -> str | None:
        """
        トークンから親招待のメールアドレスを取得
        招待が存在し、期限内の場合のみメールアドレスを返す
        """
        invite = self.parent_invite_repo.get_by_token(token)
        if not invite:
            raise ResourceNotFoundException(
                "ParentInvite",
                f"Token '{token}' not found in database.",
            )

        # 期限チェック
        now = datetime.now(UTC)
        if invite.expires_at < now:
            raise InvalidAmountException(0, "Invitation expired")

        if invite.status != "pending":
            raise InvalidAmountException(
                0,
                f"Invitation is {invite.status}. Only pending invitations are valid.",
            )

        return invite.email

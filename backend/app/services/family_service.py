import secrets
from datetime import UTC, datetime, timedelta

from injector import inject

from app.core.config import frontend_settings
from app.core.exceptions import BusinessRuleViolationException, ResourceNotFoundException
from app.domain.entities import ChildInvite, Family, FamilyMember, ParentInvite
from app.repositories.interfaces import (
    ChildInviteRepository,
    FamilyMemberRepository,
    FamilyRepository,
    ParentInviteRepository,
)
from app.services.mailer import Mailer

_INVITE_EXPIRE_DAYS = 7


class FamilyService:
    """家族管理・招待・参加のビジネスロジックサービス"""

    @inject
    def __init__(
        self,
        family_repo: FamilyRepository,
        member_repo: FamilyMemberRepository,
        parent_invite_repo: ParentInviteRepository,
        child_invite_repo: ChildInviteRepository,
        mailer: Mailer,
    ):
        self.family_repo = family_repo
        self.member_repo = member_repo
        self.parent_invite_repo = parent_invite_repo
        self.child_invite_repo = child_invite_repo
        self.mailer = mailer

    # ── 家族取得 ────────────────────────────────────────────────

    def get_family(self, family_id: str) -> Family | None:
        """IDで家族を取得"""
        return self.family_repo.get_by_id(family_id)

    def get_members(self, family_id: str) -> list[FamilyMember]:
        """家族の全メンバーを取得"""
        return self.member_repo.list_members(family_id)

    def get_member(self, uid: str) -> FamilyMember | None:
        """Firebase Auth UID でメンバーを取得（どの家族でも）"""
        return self.member_repo.get_by_auth_uid(uid)

    # ── 家族作成（初回登録） ────────────────────────────────────

    def create_family_with_parent(
        self,
        uid: str,
        name: str,
        email: str,
        family_name: str | None = None,
    ) -> tuple[Family, FamilyMember]:
        """新しい家族を作成し、呼び出し元ユーザーを親メンバーとして追加"""
        family = self.family_repo.create(name=family_name)
        member = self.member_repo.create(
            family_id=family.id,
            uid=uid,
            name=name,
            role="parent",
            email=email,
        )
        return family, member

    # ── 親招待（子 → 親） ───────────────────────────────────────

    def invite_parent(
        self,
        family_id: str,
        inviter_uid: str,
        email: str,
    ) -> ParentInvite:
        """親を家族に招待するトークンを発行（子が発行）"""
        inviter = self.member_repo.get_by_uid(family_id, inviter_uid)
        if not inviter:
            raise ResourceNotFoundException("FamilyMember", inviter_uid)

        token = secrets.token_urlsafe(32)
        now = datetime.now(UTC)
        expires_at = now + timedelta(days=_INVITE_EXPIRE_DAYS)

        invite = self.parent_invite_repo.create(
            token=token,
            family_id=family_id,
            inviter_uid=inviter_uid,
            email=email,
            expires_at=expires_at,
            created_at=now,
        )

        accept_link = f"{frontend_settings.origin}/accept-invite?token={token}"
        self.mailer.send_parent_invite(
            email,
            accept_link,
            inviter_name=inviter.name,
            child_name=inviter.name,
        )
        return invite

    def accept_parent_invite(
        self,
        token: str,
        uid: str,
        name: str,
        email: str,
    ) -> FamilyMember:
        """親招待を承認し、呼び出し元を parent メンバーとして追加"""
        invite = self.parent_invite_repo.get_by_token(token)
        if not invite:
            raise ResourceNotFoundException("ParentInvite", token)
        if invite.accepted_at is not None:
            raise BusinessRuleViolationException("invite_already_accepted", "Invite already accepted")
        if invite.expires_at < datetime.now(UTC):
            raise BusinessRuleViolationException("invite_expired", "Invite expired")

        member = self.member_repo.create(
            family_id=invite.family_id,
            uid=uid,
            name=name,
            role="parent",
            email=email,
        )
        self.parent_invite_repo.mark_accepted(token, datetime.now(UTC))
        return member

    # ── 子招待（親 → 子） ───────────────────────────────────────

    def invite_child(
        self,
        family_id: str,
        inviter_uid: str,
        child_name: str,
    ) -> ChildInvite:
        """子供を家族に招待するトークンを発行（親が発行）"""
        inviter = self.member_repo.get_by_uid(family_id, inviter_uid)
        if not inviter or inviter.role != "parent":
            raise BusinessRuleViolationException("parent_only", "Only parents can invite children")

        token = secrets.token_urlsafe(32)
        now = datetime.now(UTC)
        expires_at = now + timedelta(days=_INVITE_EXPIRE_DAYS)

        return self.child_invite_repo.create(
            token=token,
            family_id=family_id,
            inviter_uid=inviter_uid,
            child_name=child_name,
            expires_at=expires_at,
            created_at=now,
        )

    def accept_child_invite(
        self,
        token: str,
        uid: str,
    ) -> FamilyMember:
        """子招待を承認し、呼び出し元を child メンバーとして追加"""
        invite = self.child_invite_repo.get_by_token(token)
        if not invite:
            raise ResourceNotFoundException("ChildInvite", token)
        if invite.accepted_at is not None:
            raise BusinessRuleViolationException("invite_already_accepted", "Invite already accepted")
        if invite.expires_at < datetime.now(UTC):
            raise BusinessRuleViolationException("invite_expired", "Invite expired")

        member = self.member_repo.create(
            family_id=invite.family_id,
            uid=uid,
            name=invite.child_name,
            role="child",
            email=None,
        )
        self.child_invite_repo.mark_accepted(token, datetime.now(UTC))
        return member

"""
ChildInviteRepositoryのSQLAlchemy実装
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.domain import entities as domain
from app.repositories.interfaces import ChildInviteRepository
from app.repositories.sqlalchemy import models as db_models
from app.repositories.sqlalchemy.mapper import to_domain_child_invite


class SQLAlchemyChildInviteRepository(ChildInviteRepository):
    """ChildInviteRepositoryのSQLAlchemy実装"""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        child_id: str,
        email: str,
        token: str,
        expires_at: datetime,
    ) -> domain.ChildInvite:
        """子ども招待を作成"""
        db_invite = db_models.ChildInvite(
            token=token,
            child_id=child_id,
            email=email,
            status="pending",
            expires_at=expires_at.replace(tzinfo=UTC),
            created_at=datetime.now(UTC),
        )
        self.db.add(db_invite)
        self.db.flush()
        self.db.refresh(db_invite)
        return to_domain_child_invite(db_invite)

    def get_by_token(self, token: str) -> domain.ChildInvite | None:
        """トークンで子ども招待を取得"""
        db_invite = (
            self.db.query(db_models.ChildInvite)
            .filter(db_models.ChildInvite.token == token)
            .first()
        )
        return to_domain_child_invite(db_invite) if db_invite else None

    def update_status(self, invite: domain.ChildInvite, status: str) -> domain.ChildInvite:
        """子ども招待のステータスを更新"""
        db_invite = self.db.query(db_models.ChildInvite).get(invite.id)
        if not db_invite:
            return invite
        db_invite.status = status  # type: ignore
        self.db.flush()
        self.db.refresh(db_invite)
        return to_domain_child_invite(db_invite)

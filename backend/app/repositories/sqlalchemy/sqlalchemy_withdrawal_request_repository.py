"""
WithdrawalRequestRepositoryのSQLAlchemy実装
"""

import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.domain.entities import WithdrawalRequest
from app.repositories.interfaces import WithdrawalRequestRepository
from app.repositories.sqlalchemy import models as db_models
from app.repositories.sqlalchemy.mapper import to_domain_withdrawal_request


class SQLAlchemyWithdrawalRequestRepository(WithdrawalRequestRepository):
    """WithdrawalRequestRepositoryのSQLAlchemy実装"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, request_id: str) -> WithdrawalRequest | None:
        """IDで出金リクエストを取得"""
        db_request = (
            self.db.query(db_models.WithdrawalRequest)
            .filter(db_models.WithdrawalRequest.id == uuid.UUID(request_id))
            .first()
        )
        return to_domain_withdrawal_request(db_request) if db_request else None

    def get_pending_by_parent(self, parent_id: str) -> list[WithdrawalRequest]:
        """親の子供の全ての保留中出金リクエストを取得"""
        db_requests = (
            self.db.query(db_models.WithdrawalRequest)
            .join(
                db_models.Account,
                db_models.WithdrawalRequest.account_id == db_models.Account.id,
            )
            .join(db_models.Profile, db_models.Account.user_id == db_models.Profile.id)
            .join(
                db_models.FamilyRelationship,
                db_models.Profile.id == db_models.FamilyRelationship.child_id,
            )
            .filter(db_models.FamilyRelationship.parent_id == uuid.UUID(parent_id))
            .filter(db_models.WithdrawalRequest.status == "pending")
            .order_by(db_models.WithdrawalRequest.created_at.desc())
            .all()
        )
        return [to_domain_withdrawal_request(r) for r in db_requests]

    def create(
        self,
        account_id: str,
        amount: int,
        description: str | None,
        created_at: datetime,
    ) -> WithdrawalRequest:
        """新規出金リクエストを作成"""
        db_request = db_models.WithdrawalRequest(
            id=uuid.uuid4(),
            account_id=uuid.UUID(account_id),
            amount=amount,
            description=description,
            status="pending",
            created_at=str(created_at),
            updated_at=str(created_at),
        )
        self.db.add(db_request)
        self.db.flush()
        self.db.refresh(db_request)
        return to_domain_withdrawal_request(db_request)

    def update_status(
        self, request: WithdrawalRequest, status: str, updated_at: datetime
    ) -> WithdrawalRequest:
        """出金リクエストのステータスを更新"""
        db_request = (
            self.db.query(db_models.WithdrawalRequest)
            .filter(db_models.WithdrawalRequest.id == uuid.UUID(request.id))
            .first()
        )
        if db_request:
            db_request.status = status  # type: ignore
            db_request.updated_at = str(updated_at)  # type: ignore
            self.db.flush()
            self.db.refresh(db_request)
            return to_domain_withdrawal_request(db_request)
        raise ValueError(f"WithdrawalRequest {request.id} not found")

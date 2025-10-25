"""
WithdrawalRequestRepositoryのSQLAlchemy実装
"""

import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.models import Account, Profile, WithdrawalRequest
from app.repositories.interfaces import WithdrawalRequestRepository


class SQLAlchemyWithdrawalRequestRepository(WithdrawalRequestRepository):
    """WithdrawalRequestRepositoryのSQLAlchemy実装"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, request_id: str) -> WithdrawalRequest | None:
        """IDで出金リクエストを取得"""
        return (
            self.db.query(WithdrawalRequest)
            .filter(WithdrawalRequest.id == uuid.UUID(request_id))
            .first()
        )

    def get_pending_by_parent(self, parent_id: str) -> list[WithdrawalRequest]:
        """親の子供の全ての保留中出金リクエストを取得"""
        return list(
            self.db.query(WithdrawalRequest)
            .join(Account, WithdrawalRequest.account_id == Account.id)
            .join(Profile, Account.user_id == Profile.id)
            .filter(Profile.parent_id == uuid.UUID(parent_id))
            .filter(WithdrawalRequest.status == "pending")
            .order_by(WithdrawalRequest.created_at.desc())
            .all()
        )

    def create(
        self,
        account_id: str,
        amount: int,
        description: str | None,
        created_at: datetime,
    ) -> WithdrawalRequest:
        """新規出金リクエストを作成"""
        request = WithdrawalRequest(
            id=uuid.uuid4(),
            account_id=uuid.UUID(account_id),
            amount=amount,
            description=description,
            status="pending",
            created_at=str(created_at),
            updated_at=str(created_at),
        )
        self.db.add(request)
        self.db.flush()
        self.db.refresh(request)
        return request

    def update_status(
        self, request: WithdrawalRequest, status: str, updated_at: datetime
    ) -> WithdrawalRequest:
        """出金リクエストのステータスを更新"""
        request.status = status  # type: ignore
        request.updated_at = str(updated_at)  # type: ignore
        self.db.flush()
        self.db.refresh(request)
        return request

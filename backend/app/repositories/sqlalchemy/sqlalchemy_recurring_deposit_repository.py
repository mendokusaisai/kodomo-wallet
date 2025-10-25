"""
RecurringDepositRepositoryのSQLAlchemy実装
"""

import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.models import RecurringDeposit
from app.repositories.interfaces import RecurringDepositRepository


class SQLAlchemyRecurringDepositRepository(RecurringDepositRepository):
    """RecurringDepositRepositoryのSQLAlchemy実装"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_account_id(self, account_id: str) -> RecurringDeposit | None:
        """アカウントIDで定期入金設定を取得"""
        return (
            self.db.query(RecurringDeposit)
            .filter(RecurringDeposit.account_id == uuid.UUID(account_id))
            .first()
        )

    def create(
        self,
        account_id: str,
        amount: int,
        day_of_month: int,
        created_at: datetime,
    ) -> RecurringDeposit:
        """新規定期入金設定を作成"""
        recurring_deposit = RecurringDeposit(
            account_id=uuid.UUID(account_id),
            amount=amount,
            day_of_month=day_of_month,
            is_active="true",
            created_at=str(created_at),
            updated_at=str(created_at),
        )
        self.db.add(recurring_deposit)
        self.db.flush()
        self.db.refresh(recurring_deposit)
        return recurring_deposit

    def update(
        self,
        recurring_deposit: RecurringDeposit,
        amount: int | None,
        day_of_month: int | None,
        is_active: bool | None,
        updated_at: datetime,
    ) -> RecurringDeposit:
        """定期入金設定を更新"""
        if amount is not None:
            recurring_deposit.amount = amount  # type: ignore
        if day_of_month is not None:
            recurring_deposit.day_of_month = day_of_month  # type: ignore
        if is_active is not None:
            recurring_deposit.is_active = "true" if is_active else "false"  # type: ignore
        recurring_deposit.updated_at = str(updated_at)  # type: ignore
        self.db.flush()
        self.db.refresh(recurring_deposit)
        return recurring_deposit

    def delete(self, recurring_deposit: RecurringDeposit) -> bool:
        """定期入金設定を削除"""
        self.db.delete(recurring_deposit)
        self.db.flush()
        return True

"""
RecurringDepositRepositoryのSQLAlchemy実装
"""

import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.domain.entities import RecurringDeposit
from app.repositories.interfaces import RecurringDepositRepository
from app.repositories.sqlalchemy import models as db_models
from app.repositories.sqlalchemy.mapper import to_domain_recurring_deposit


class SQLAlchemyRecurringDepositRepository(RecurringDepositRepository):
    """RecurringDepositRepositoryのSQLAlchemy実装"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_account_id(self, account_id: str) -> RecurringDeposit | None:
        """アカウントIDで定期入金設定を取得"""
        db_deposit = (
            self.db.query(db_models.RecurringDeposit)
            .filter(db_models.RecurringDeposit.account_id == uuid.UUID(account_id))
            .first()
        )
        return to_domain_recurring_deposit(db_deposit) if db_deposit else None

    def create(
        self,
        account_id: str,
        amount: int,
        day_of_month: int,
        created_at: datetime,
    ) -> RecurringDeposit:
        """新規定期入金設定を作成"""
        db_deposit = db_models.RecurringDeposit(
            account_id=uuid.UUID(account_id),
            amount=amount,
            day_of_month=day_of_month,
            is_active="true",
            created_at=str(created_at),
            updated_at=str(created_at),
        )
        self.db.add(db_deposit)
        self.db.flush()
        self.db.refresh(db_deposit)
        return to_domain_recurring_deposit(db_deposit)

    def update(
        self,
        recurring_deposit: RecurringDeposit,
        amount: int | None,
        day_of_month: int | None,
        is_active: bool | None,
        updated_at: datetime,
    ) -> RecurringDeposit:
        """定期入金設定を更新"""
        db_deposit = (
            self.db.query(db_models.RecurringDeposit)
            .filter(db_models.RecurringDeposit.id == uuid.UUID(recurring_deposit.id))
            .first()
        )

        if not db_deposit:
            raise ValueError(f"RecurringDeposit {recurring_deposit.id} not found")

        if amount is not None:
            db_deposit.amount = amount  # type: ignore
        if day_of_month is not None:
            db_deposit.day_of_month = day_of_month  # type: ignore
        if is_active is not None:
            db_deposit.is_active = "true" if is_active else "false"  # type: ignore
        db_deposit.updated_at = str(updated_at)  # type: ignore
        self.db.flush()
        self.db.refresh(db_deposit)
        return to_domain_recurring_deposit(db_deposit)

    def delete(self, recurring_deposit: RecurringDeposit) -> bool:
        """定期入金設定を削除"""
        db_deposit = (
            self.db.query(db_models.RecurringDeposit)
            .filter(db_models.RecurringDeposit.id == uuid.UUID(recurring_deposit.id))
            .first()
        )
        if not db_deposit:
            return False
        self.db.delete(db_deposit)
        self.db.flush()
        return True

"""RecurringDepositExecution用SQLAlchemyリポジトリ実装"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.domain.entities import RecurringDepositExecution
from app.repositories.interfaces import RecurringDepositExecutionRepository


class SQLAlchemyRecurringDepositExecutionRepository(RecurringDepositExecutionRepository):
    """RecurringDepositExecutionのSQLAlchemy実装"""

    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        recurring_deposit_id: str,
        transaction_id: str | None,
        status: str,
        amount: int,
        day_of_month: int,
        error_message: str | None,
        executed_at: datetime,
        created_at: datetime,
    ) -> RecurringDepositExecution:
        """実行履歴を作成"""
        execution_id = str(uuid4())

        query = text("""
            INSERT INTO recurring_deposit_executions (
                id, recurring_deposit_id, transaction_id, status, amount,
                day_of_month, error_message, executed_at, created_at
            )
            VALUES (:id, :recurring_deposit_id, :transaction_id, :status, :amount,
                    :day_of_month, :error_message, :executed_at, :created_at)
            RETURNING id, recurring_deposit_id, transaction_id, executed_at, status,
                      error_message, amount, day_of_month, created_at
        """)

        result = self.session.execute(
            query,
            {
                "id": execution_id,
                "recurring_deposit_id": recurring_deposit_id,
                "transaction_id": transaction_id,
                "status": status,
                "amount": amount,
                "day_of_month": day_of_month,
                "error_message": error_message,
                "executed_at": executed_at,
                "created_at": created_at,
            },
        ).fetchone()

        self.session.commit()

        if not result:
            raise RuntimeError("Failed to create recurring deposit execution")

        return RecurringDepositExecution(
            id=str(result[0]),
            recurring_deposit_id=str(result[1]),
            transaction_id=str(result[2]) if result[2] else None,
            executed_at=result[3],
            status=result[4],
            error_message=result[5],
            amount=result[6],
            day_of_month=result[7],
            created_at=result[8],
        )

    def has_execution_this_month(self, recurring_deposit_id: str, year: int, month: int) -> bool:
        """指定した年月に成功した実行履歴が存在するかチェック"""
        query = text("""
            SELECT COUNT(*) > 0
            FROM recurring_deposit_executions
            WHERE recurring_deposit_id = :recurring_deposit_id
              AND status = 'success'
              AND EXTRACT(YEAR FROM executed_at) = :year
              AND EXTRACT(MONTH FROM executed_at) = :month
        """)

        result = self.session.execute(
            query,
            {
                "recurring_deposit_id": recurring_deposit_id,
                "year": year,
                "month": month,
            },
        ).scalar()

        return bool(result)

    def get_by_recurring_deposit_id(
        self, recurring_deposit_id: str, limit: int = 10
    ) -> list[RecurringDepositExecution]:
        """定期入金設定IDで実行履歴を取得（最新順）"""
        query = text("""
            SELECT id, recurring_deposit_id, transaction_id, executed_at, status,
                   error_message, amount, day_of_month, created_at
            FROM recurring_deposit_executions
            WHERE recurring_deposit_id = :recurring_deposit_id
            ORDER BY executed_at DESC
            LIMIT :limit
        """)

        results = self.session.execute(
            query,
            {
                "recurring_deposit_id": recurring_deposit_id,
                "limit": limit,
            },
        ).fetchall()

        return [
            RecurringDepositExecution(
                id=str(row[0]),
                recurring_deposit_id=str(row[1]),
                transaction_id=str(row[2]) if row[2] else None,
                executed_at=row[3],
                status=row[4],
                error_message=row[5],
                amount=row[6],
                day_of_month=row[7],
                created_at=row[8],
            )
            for row in results
        ]

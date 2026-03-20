"""Firestore 実装: RecurringDepositRepository"""

from dataclasses import replace
from datetime import UTC, datetime
from uuid import uuid4

from app.core.database import get_firestore_client
from app.domain.entities import RecurringDeposit
from app.repositories.interfaces import RecurringDepositRepository


class FirestoreRecurringDepositRepository(RecurringDepositRepository):
    """Firestore バックエンドの RecurringDepositRepository 実装

    データパス: recurringDeposits/{id}
    """

    def __init__(self) -> None:
        self._db = get_firestore_client()

    def _col(self):
        return self._db.collection("recurringDeposits")

    def get_by_id(self, recurring_deposit_id: str) -> RecurringDeposit | None:
        doc = self._col().document(recurring_deposit_id).get()
        if not doc.exists:
            return None
        return self._to_entity(doc.id, doc.to_dict())

    def get_by_account_id(self, family_id: str, account_id: str) -> RecurringDeposit | None:
        docs = list(
            self._col()
            .where("familyId", "==", family_id)
            .where("accountId", "==", account_id)
            .where("isActive", "==", True)
            .limit(1)
            .stream()
        )
        if not docs:
            return None
        return self._to_entity(docs[0].id, docs[0].to_dict())

    def create(
        self,
        family_id: str,
        account_id: str,
        amount: int,
        interval_days: int,
        next_execute_at: datetime,
        created_by_uid: str,
        created_at: datetime,
    ) -> RecurringDeposit:
        rd_id = str(uuid4())
        data = {
            "familyId": family_id,
            "accountId": account_id,
            "amount": amount,
            "intervalDays": interval_days,
            "nextExecuteAt": next_execute_at,
            "isActive": True,
            "createdByUid": created_by_uid,
            "createdAt": created_at,
        }
        self._col().document(rd_id).set(data)
        return RecurringDeposit(
            id=rd_id,
            family_id=family_id,
            account_id=account_id,
            amount=amount,
            interval_days=interval_days,
            next_execute_at=next_execute_at,
            is_active=True,
            created_at=created_at,
            created_by_uid=created_by_uid,
        )

    def update(
        self,
        recurring_deposit: RecurringDeposit,
        amount: int | None,
        interval_days: int | None,
        is_active: bool | None,
        next_execute_at: datetime | None,
    ) -> RecurringDeposit:
        updates: dict = {}
        if amount is not None:
            updates["amount"] = amount
        if interval_days is not None:
            updates["intervalDays"] = interval_days
        if is_active is not None:
            updates["isActive"] = is_active
        if next_execute_at is not None:
            updates["nextExecuteAt"] = next_execute_at
        if updates:
            self._col().document(recurring_deposit.id).update(updates)

        entity_updates = {
            k: v for k, v in {
                "amount": amount,
                "interval_days": interval_days,
                "is_active": is_active,
                "next_execute_at": next_execute_at,
            }.items() if v is not None
        }
        return replace(recurring_deposit, **entity_updates)

    def delete(self, recurring_deposit_id: str) -> bool:
        ref = self._col().document(recurring_deposit_id)
        doc = ref.get()
        if not doc.exists:
            return False
        ref.delete()
        return True

    def get_due(self, now: datetime) -> list[RecurringDeposit]:
        docs = (
            self._col()
            .where("isActive", "==", True)
            .where("nextExecuteAt", "<=", now)
            .stream()
        )
        return [self._to_entity(d.id, d.to_dict()) for d in docs]

    @staticmethod
    def _to_entity(doc_id: str, data: dict) -> RecurringDeposit:
        def _dt(val):
            if val is None:
                return datetime.now(UTC)
            if hasattr(val, "ToDatetime"):
                return val.ToDatetime(tzinfo=UTC)
            return val

        return RecurringDeposit(
            id=doc_id,
            family_id=data.get("familyId", ""),
            account_id=data.get("accountId", ""),
            amount=data.get("amount", 0),
            interval_days=data.get("intervalDays", 7),
            next_execute_at=_dt(data.get("nextExecuteAt")),
            is_active=data.get("isActive", True),
            created_at=_dt(data.get("createdAt")),
            created_by_uid=data.get("createdByUid", ""),
        )

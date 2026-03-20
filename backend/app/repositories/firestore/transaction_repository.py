"""Firestore 実装: TransactionRepository"""

from datetime import UTC, datetime
from uuid import uuid4

from app.core.database import get_firestore_client
from app.domain.entities import Transaction
from app.repositories.interfaces import TransactionRepository


class FirestoreTransactionRepository(TransactionRepository):
    """Firestore バックエンドの TransactionRepository 実装

    データパス: families/{familyId}/accounts/{accountId}/transactions/{txId}
    """

    def __init__(self) -> None:
        self._db = get_firestore_client()

    def _transactions(self, family_id: str, account_id: str):
        return (
            self._db.collection("families")
            .document(family_id)
            .collection("accounts")
            .document(account_id)
            .collection("transactions")
        )

    def get_by_account_id(
        self, family_id: str, account_id: str, limit: int = 50
    ) -> list[Transaction]:
        docs = (
            self._transactions(family_id, account_id)
            .order_by("createdAt", direction="DESCENDING")
            .limit(limit)
            .stream()
        )
        return [self._to_entity(d.id, family_id, account_id, d.to_dict()) for d in docs]

    def create(
        self,
        family_id: str,
        account_id: str,
        transaction_type: str,
        amount: int,
        note: str | None,
        created_by_uid: str,
        created_at: datetime,
    ) -> Transaction:
        tx_id = str(uuid4())
        data = {
            "type": transaction_type,
            "amount": amount,
            "note": note,
            "createdByUid": created_by_uid,
            "createdAt": created_at,
        }
        self._transactions(family_id, account_id).document(tx_id).set(data)
        return Transaction(
            id=tx_id,
            account_id=account_id,
            family_id=family_id,
            type=transaction_type,  # type: ignore
            amount=amount,
            note=note,
            created_at=created_at,
            created_by_uid=created_by_uid,
        )

    @staticmethod
    def _to_entity(
        tx_id: str, family_id: str, account_id: str, data: dict
    ) -> Transaction:
        def _dt(val):
            if val is None:
                return datetime.now(UTC)
            if hasattr(val, "ToDatetime"):
                return val.ToDatetime(tzinfo=UTC)
            return val

        return Transaction(
            id=tx_id,
            account_id=account_id,
            family_id=family_id,
            type=data.get("type", "deposit"),  # type: ignore
            amount=data.get("amount", 0),
            note=data.get("note"),
            created_at=_dt(data.get("createdAt")),
            created_by_uid=data.get("createdByUid", ""),
        )

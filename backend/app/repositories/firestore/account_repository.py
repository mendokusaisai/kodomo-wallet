"""Firestore 実装: AccountRepository"""

from datetime import UTC, datetime
from uuid import uuid4

from app.core.database import get_firestore_client
from app.domain.entities import Account
from app.repositories.interfaces import AccountRepository


class FirestoreAccountRepository(AccountRepository):
    """Firestore バックエンドの AccountRepository 実装

    データパス: families/{familyId}/accounts/{accountId}
    """

    def __init__(self) -> None:
        self._db = get_firestore_client()

    def _accounts(self, family_id: str):
        return self._db.collection("families").document(family_id).collection("accounts")

    def get_by_family_id(self, family_id: str) -> list[Account]:
        docs = self._accounts(family_id).stream()
        return [self._to_entity(d.id, family_id, d.to_dict()) for d in docs]

    def get_by_id(self, family_id: str, account_id: str) -> Account | None:
        doc = self._accounts(family_id).document(account_id).get()
        if not doc.exists:
            return None
        return self._to_entity(doc.id, family_id, doc.to_dict())

    def create(
        self,
        family_id: str,
        name: str,
        balance: int = 0,
        currency: str = "JPY",
    ) -> Account:
        account_id = str(uuid4())
        now = datetime.now(UTC)
        data = {
            "name": name,
            "balance": balance,
            "currency": currency,
            "goalName": None,
            "goalAmount": None,
            "createdAt": now,
            "updatedAt": now,
        }
        self._accounts(family_id).document(account_id).set(data)
        return Account(
            id=account_id,
            family_id=family_id,
            name=name,
            balance=balance,
            currency=currency,
            goal_name=None,
            goal_amount=None,
            created_at=now,
            updated_at=now,
        )

    def update(self, account: Account) -> Account:
        now = datetime.now(UTC)
        data = {
            "name": account.name,
            "goalName": account.goal_name,
            "goalAmount": account.goal_amount,
            "updatedAt": now,
        }
        self._accounts(account.family_id).document(account.id).update(data)
        return account

    def update_balance(self, account: Account, new_balance: int) -> None:
        now = datetime.now(UTC)
        self._accounts(account.family_id).document(account.id).update({
            "balance": new_balance,
            "updatedAt": now,
        })

    def delete(self, family_id: str, account_id: str) -> bool:
        ref = self._accounts(family_id).document(account_id)
        doc = ref.get()
        if not doc.exists:
            return False
        ref.delete()
        return True

    @staticmethod
    def _to_entity(account_id: str, family_id: str, data: dict) -> Account:
        def _dt(val):
            if val is None:
                return datetime.now(UTC)
            if hasattr(val, "ToDatetime"):
                return val.ToDatetime(tzinfo=UTC)
            return val

        return Account(
            id=account_id,
            family_id=family_id,
            name=data.get("name", ""),
            balance=data.get("balance", 0),
            currency=data.get("currency", "JPY"),
            goal_name=data.get("goalName"),
            goal_amount=data.get("goalAmount"),
            created_at=_dt(data.get("createdAt")),
            updated_at=_dt(data.get("updatedAt")),
        )

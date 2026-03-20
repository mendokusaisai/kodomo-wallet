"""Firestore 実装: FamilyRepository"""

from datetime import UTC, datetime
from uuid import uuid4

from firebase_admin import firestore as fs

from app.core.database import get_firestore_client
from app.domain.entities import Family
from app.repositories.interfaces import FamilyRepository


class FirestoreFamilyRepository(FamilyRepository):
    """Firestore バックエンドの FamilyRepository 実装"""

    def __init__(self) -> None:
        self._db = get_firestore_client()

    def _col(self):
        return self._db.collection("families")

    def get_by_id(self, family_id: str) -> Family | None:
        doc = self._col().document(family_id).get()
        if not doc.exists:
            return None
        return self._to_entity(doc.id, doc.to_dict())

    def create(self, name: str | None = None) -> Family:
        family_id = str(uuid4())
        now = datetime.now(UTC)
        data = {
            "name": name,
            "createdAt": now,
        }
        self._col().document(family_id).set(data)
        return Family(id=family_id, name=name, created_at=now)

    @staticmethod
    def _to_entity(doc_id: str, data: dict) -> Family:
        created_at = data.get("createdAt")
        if hasattr(created_at, "ToDatetime"):
            created_at = created_at.ToDatetime(tzinfo=UTC)
        return Family(
            id=doc_id,
            name=data.get("name"),
            created_at=created_at or datetime.now(UTC),
        )

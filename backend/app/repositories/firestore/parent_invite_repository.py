"""Firestore 実装: ParentInviteRepository"""

from dataclasses import replace
from datetime import UTC, datetime

from app.core.database import get_firestore_client
from app.domain.entities import ParentInvite
from app.repositories.interfaces import ParentInviteRepository


class FirestoreParentInviteRepository(ParentInviteRepository):
    """Firestore バックエンドの ParentInviteRepository 実装

    データパス: parentInvites/{token}
    """

    def __init__(self) -> None:
        self._db = get_firestore_client()

    def _col(self):
        return self._db.collection("parentInvites")

    def get_by_token(self, token: str) -> ParentInvite | None:
        doc = self._col().document(token).get()
        if not doc.exists:
            return None
        return self._to_entity(doc.id, doc.to_dict())

    def create(
        self,
        token: str,
        family_id: str,
        inviter_uid: str,
        email: str,
        expires_at: datetime,
        created_at: datetime,
    ) -> ParentInvite:
        data = {
            "familyId": family_id,
            "inviterUid": inviter_uid,
            "email": email,
            "expiresAt": expires_at,
            "acceptedAt": None,
            "createdAt": created_at,
        }
        self._col().document(token).set(data)
        return ParentInvite(
            token=token,
            family_id=family_id,
            inviter_uid=inviter_uid,
            email=email,
            expires_at=expires_at,
            accepted_at=None,
            created_at=created_at,
        )

    def mark_accepted(self, token: str, accepted_at: datetime) -> ParentInvite:
        self._col().document(token).update({"acceptedAt": accepted_at})
        doc = self._col().document(token).get()
        return self._to_entity(doc.id, doc.to_dict())

    @staticmethod
    def _to_entity(token: str, data: dict) -> ParentInvite:
        def _dt(val):
            if val is None:
                return None
            if hasattr(val, "ToDatetime"):
                return val.ToDatetime(tzinfo=UTC)
            return val

        def _dt_required(val):
            if val is None:
                return datetime.now(UTC)
            if hasattr(val, "ToDatetime"):
                return val.ToDatetime(tzinfo=UTC)
            return val

        return ParentInvite(
            token=token,
            family_id=data.get("familyId", ""),
            inviter_uid=data.get("inviterUid", ""),
            email=data.get("email", ""),
            expires_at=_dt_required(data.get("expiresAt")),
            accepted_at=_dt(data.get("acceptedAt")),
            created_at=_dt_required(data.get("createdAt")),
        )

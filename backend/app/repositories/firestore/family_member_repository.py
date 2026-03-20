"""Firestore 実装: FamilyMemberRepository"""

from datetime import UTC, datetime

from app.core.database import get_firestore_client
from app.domain.entities import FamilyMember
from app.repositories.interfaces import FamilyMemberRepository


class FirestoreFamilyMemberRepository(FamilyMemberRepository):
    """Firestore バックエンドの FamilyMemberRepository 実装

    データパス: families/{familyId}/members/{authUid}
    """

    def __init__(self) -> None:
        self._db = get_firestore_client()

    def _members(self, family_id: str):
        return self._db.collection("families").document(family_id).collection("members")

    def get_by_uid(self, family_id: str, uid: str) -> FamilyMember | None:
        doc = self._members(family_id).document(uid).get()
        if not doc.exists:
            return None
        return self._to_entity(doc.id, family_id, doc.to_dict())

    def get_by_auth_uid(self, uid: str) -> FamilyMember | None:
        """コレクショングループ検索で全家族から uid を探す"""
        query = (
            self._db.collection_group("members")
            .where("uid", "==", uid)
            .limit(1)
        )
        docs = list(query.stream())
        if not docs:
            return None
        doc = docs[0]
        # ドキュメントパス: families/{familyId}/members/{uid}
        family_id = doc.reference.parent.parent.id
        return self._to_entity(doc.id, family_id, doc.to_dict())

    def list_members(self, family_id: str) -> list[FamilyMember]:
        docs = self._members(family_id).stream()
        return [self._to_entity(d.id, family_id, d.to_dict()) for d in docs]

    def create(
        self,
        family_id: str,
        uid: str,
        name: str,
        role: str,
        email: str | None = None,
    ) -> FamilyMember:
        now = datetime.now(UTC)
        data = {
            "uid": uid,
            "name": name,
            "role": role,
            "email": email,
            "joinedAt": now,
            "updatedAt": now,
        }
        self._members(family_id).document(uid).set(data)
        return FamilyMember(
            uid=uid,
            family_id=family_id,
            name=name,
            role=role,  # type: ignore
            email=email,
            joined_at=now,
            updated_at=now,
        )

    def update(self, member: FamilyMember) -> FamilyMember:
        now = datetime.now(UTC)
        data = {
            "name": member.name,
            "role": member.role,
            "email": member.email,
            "updatedAt": now,
        }
        self._members(member.family_id).document(member.uid).update(data)
        return member

    def delete(self, family_id: str, uid: str) -> bool:
        ref = self._members(family_id).document(uid)
        doc = ref.get()
        if not doc.exists:
            return False
        ref.delete()
        return True

    @staticmethod
    def _to_entity(uid: str, family_id: str, data: dict) -> FamilyMember:
        def _dt(val):
            if val is None:
                return datetime.now(UTC)
            if hasattr(val, "ToDatetime"):
                return val.ToDatetime(tzinfo=UTC)
            return val

        return FamilyMember(
            uid=uid,
            family_id=family_id,
            name=data.get("name", ""),
            role=data.get("role", "child"),  # type: ignore
            email=data.get("email"),
            joined_at=_dt(data.get("joinedAt")),
            updated_at=_dt(data.get("updatedAt")),
        )

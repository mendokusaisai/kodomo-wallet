import uuid
from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.entities import FamilyRelationship, Profile
from app.repositories.interfaces import FamilyRelationshipRepository
from app.repositories.sqlalchemy import models as db_models
from app.repositories.sqlalchemy.mapper import (
    to_domain_family_relationship,
    to_domain_profile,
)


class SQLAlchemyFamilyRelationshipRepository(FamilyRelationshipRepository):
    """FamilyRelationshipRepository の SQLAlchemy 実装"""

    def __init__(self, db: Session):
        self.db = db

    def get_parents(self, child_id: str) -> list[Profile]:
        db_profiles = (
            self.db.query(db_models.Profile)
            .join(
                db_models.FamilyRelationship,
                db_models.Profile.id == db_models.FamilyRelationship.parent_id,
            )
            .filter(db_models.FamilyRelationship.child_id == uuid.UUID(child_id))
            .all()
        )
        return [to_domain_profile(p) for p in db_profiles]

    def get_children(self, parent_id: str) -> list[Profile]:
        db_profiles = (
            self.db.query(db_models.Profile)
            .join(
                db_models.FamilyRelationship,
                db_models.Profile.id == db_models.FamilyRelationship.child_id,
            )
            .filter(db_models.FamilyRelationship.parent_id == uuid.UUID(parent_id))
            .all()
        )
        return [to_domain_profile(p) for p in db_profiles]

    def has_relationship(self, parent_id: str, child_id: str) -> bool:
        rel = (
            self.db.query(db_models.FamilyRelationship)
            .filter(
                db_models.FamilyRelationship.parent_id == uuid.UUID(parent_id),
                db_models.FamilyRelationship.child_id == uuid.UUID(child_id),
            )
            .first()
        )
        return rel is not None

    def add_relationship(
        self, parent_id: str, child_id: str, relationship_type: str = "parent"
    ) -> FamilyRelationship:
        rel = db_models.FamilyRelationship(
            id=uuid.uuid4(),
            parent_id=uuid.UUID(parent_id),
            child_id=uuid.UUID(child_id),
            relationship_type=relationship_type,
            created_at=str(datetime.now(UTC)),
        )
        self.db.add(rel)
        self.db.flush()
        self.db.refresh(rel)
        return to_domain_family_relationship(rel)  # type: ignore

    def remove_relationship(self, parent_id: str, child_id: str) -> bool:
        deleted = (
            self.db.query(db_models.FamilyRelationship)
            .filter(
                db_models.FamilyRelationship.parent_id == uuid.UUID(parent_id),
                db_models.FamilyRelationship.child_id == uuid.UUID(child_id),
            )
            .delete()
        )
        return deleted > 0

    def get_relationship(self, parent_id: str, child_id: str) -> FamilyRelationship | None:
        rel = (
            self.db.query(db_models.FamilyRelationship)
            .filter(
                db_models.FamilyRelationship.parent_id == uuid.UUID(parent_id),
                db_models.FamilyRelationship.child_id == uuid.UUID(child_id),
            )
            .first()
        )
        return to_domain_family_relationship(rel) if rel else None

    def get_related_parents(self, parent_id: str) -> list[str]:
        """
        指定した親と同じ子どもを持つ他の親のIDリストを取得

        Args:
            parent_id: 基準となる親のID

        Returns:
            家族関係にある他の親のIDリスト
        """
        # ステップ1: parent_id が持つ全子どもを取得
        children = (
            self.db.query(db_models.FamilyRelationship.child_id)
            .filter(db_models.FamilyRelationship.parent_id == uuid.UUID(parent_id))
            .all()
        )

        if not children:
            return []

        child_ids = [c.child_id for c in children]

        # ステップ2: それらの子どもを持つ他の親を取得
        other_parents = (
            self.db.query(db_models.FamilyRelationship.parent_id)
            .filter(db_models.FamilyRelationship.child_id.in_(child_ids))
            .filter(db_models.FamilyRelationship.parent_id != uuid.UUID(parent_id))
            .distinct()
            .all()
        )

        return [str(p.parent_id) for p in other_parents]

    def create_relationship(self, parent_id: str, child_id: str) -> None:
        """
        親子関係を作成(重複は無視)

        Args:
            parent_id: 親のID
            child_id: 子どものID

        Note:
            既に同じ関係が存在する場合は何もしない(エラーにならない)
        """
        relationship = db_models.FamilyRelationship(
            parent_id=uuid.UUID(parent_id),
            child_id=uuid.UUID(child_id),
            relationship_type="parent",
            created_at=str(datetime.now(UTC)),
        )
        self.db.add(relationship)

        try:
            self.db.flush()
        except IntegrityError:
            # UNIQUE制約違反 = 既に関係が存在 → 無視
            self.db.rollback()

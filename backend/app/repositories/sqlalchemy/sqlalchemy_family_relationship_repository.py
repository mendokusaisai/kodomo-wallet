import uuid
from datetime import UTC, datetime

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

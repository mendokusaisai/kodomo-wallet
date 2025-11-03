"""
GraphQL Profile.parents フィールドの統合テスト

子プロフィールを取得し、FamilyRelationshipRepository.get_parents が
正しく複数の親を返すことを検証します。
"""

from datetime import UTC, datetime

from app.repositories.sqlalchemy import models as db_models
from app.services import ProfileService


class TestProfileParentsLogic:
    """Profile の parents ロジック（FamilyRelationshipRepository）の統合テスト"""

    def test_get_parents_with_no_parents(self, graphql_context):
        """親が存在しない子プロフィールの場合、空配列が返される"""
        # Arrange: 親なしの子プロフィールを作成
        db = graphql_context["db"]
        profile_service: ProfileService = graphql_context["profile_service"]

        now = datetime.now(UTC)
        child_profile_db = db_models.Profile(
            name="Orphan Child",
            role="child",
            avatar_url=None,
            created_at=now,
            updated_at=now,
        )
        db.add(child_profile_db)
        db.commit()
        db.refresh(child_profile_db)

        # Act: FamilyRelationshipRepository から親一覧を取得
        parents = profile_service.family_relationship_repo.get_parents(str(child_profile_db.id))

        # Assert: 親は存在しないので空配列
        assert parents == []

    def test_get_parents_with_single_parent(self, graphql_context):
        """1人の親を持つ子プロフィールの場合、親が配列で返される"""
        # Arrange: 親と子を作成し、関係を設定
        db = graphql_context["db"]
        profile_service: ProfileService = graphql_context["profile_service"]

        now = datetime.now(UTC)

        # 親プロフィール作成
        parent_profile_db = db_models.Profile(
            name="Parent One",
            role="parent",
            avatar_url=None,
            created_at=now,
            updated_at=now,
        )
        db.add(parent_profile_db)
        db.commit()
        db.refresh(parent_profile_db)

        # 子プロフィール作成
        child_profile_db = db_models.Profile(
            name="Child One",
            role="child",
            avatar_url=None,
            created_at=now,
            updated_at=now,
        )
        db.add(child_profile_db)
        db.commit()
        db.refresh(child_profile_db)

        # 親子関係を作成
        relationship = db_models.FamilyRelationship(
            parent_id=parent_profile_db.id,
            child_id=child_profile_db.id,
            relationship_type="parent",
            created_at=now,
        )
        db.add(relationship)
        db.commit()

        # Act: FamilyRelationshipRepository から親一覧を取得
        parents = profile_service.family_relationship_repo.get_parents(str(child_profile_db.id))

        # Assert: 1人の親が配列で返される
        assert len(parents) == 1
        assert parents[0].id == str(parent_profile_db.id)
        assert parents[0].name == "Parent One"
        assert parents[0].role == "parent"
        # email は profiles テーブルにないため None
        assert parents[0].email is None

    def test_get_parents_with_two_parents(self, graphql_context):
        """2人の親を持つ子プロフィールの場合、両親が配列で返される"""
        # Arrange: 2人の親と1人の子を作成し、関係を設定
        db = graphql_context["db"]
        profile_service: ProfileService = graphql_context["profile_service"]

        now = datetime.now(UTC)

        # 親1作成
        parent1_db = db_models.Profile(
            name="Parent One",
            role="parent",
            avatar_url=None,
            created_at=now,
            updated_at=now,
        )
        db.add(parent1_db)

        # 親2作成
        parent2_db = db_models.Profile(
            name="Parent Two",
            role="parent",
            avatar_url=None,
            created_at=now,
            updated_at=now,
        )
        db.add(parent2_db)
        db.commit()
        db.refresh(parent1_db)
        db.refresh(parent2_db)

        # 子プロフィール作成
        child_profile_db = db_models.Profile(
            name="Child Shared",
            role="child",
            avatar_url=None,
            created_at=now,
            updated_at=now,
        )
        db.add(child_profile_db)
        db.commit()
        db.refresh(child_profile_db)

        # 親子関係を2つ作成
        relationship1 = db_models.FamilyRelationship(
            parent_id=parent1_db.id,
            child_id=child_profile_db.id,
            relationship_type="parent",
            created_at=now,
        )
        relationship2 = db_models.FamilyRelationship(
            parent_id=parent2_db.id,
            child_id=child_profile_db.id,
            relationship_type="parent",
            created_at=now,
        )
        db.add(relationship1)
        db.add(relationship2)
        db.commit()

        # Act: FamilyRelationshipRepository から親一覧を取得
        parents = profile_service.family_relationship_repo.get_parents(str(child_profile_db.id))

        # Assert: 2人の親が配列で返される
        assert len(parents) == 2
        parent_ids = {p.id for p in parents}
        assert str(parent1_db.id) in parent_ids
        assert str(parent2_db.id) in parent_ids

        parent_names = {p.name for p in parents}
        assert "Parent One" in parent_names
        assert "Parent Two" in parent_names

    def test_get_parents_for_parent_profile(self, graphql_context):
        """親プロフィール自身は parents が空配列であることを確認"""
        # Arrange: 親プロフィールのみ作成
        db = graphql_context["db"]
        profile_service: ProfileService = graphql_context["profile_service"]

        now = datetime.now(UTC)
        parent_profile_db = db_models.Profile(
            name="Solo Parent",
            role="parent",
            avatar_url=None,
            created_at=now,
            updated_at=now,
        )
        db.add(parent_profile_db)
        db.commit()
        db.refresh(parent_profile_db)

        # Act: FamilyRelationshipRepository から親一覧を取得
        parents = profile_service.family_relationship_repo.get_parents(str(parent_profile_db.id))

        # Assert: 親自身は子ではないため、parents は空配列
        assert parents == []

    def test_has_relationship_with_two_parents(self, graphql_context):
        """has_relationship が両親に対して true を返すことを確認"""
        # Arrange: 2人の親と1人の子を作成し、関係を設定
        db = graphql_context["db"]
        profile_service: ProfileService = graphql_context["profile_service"]

        now = datetime.now(UTC)

        # 親1作成
        parent1_db = db_models.Profile(
            name="Parent One",
            role="parent",
            avatar_url=None,
            created_at=now,
            updated_at=now,
        )
        db.add(parent1_db)

        # 親2作成
        parent2_db = db_models.Profile(
            name="Parent Two",
            role="parent",
            avatar_url=None,
            created_at=now,
            updated_at=now,
        )
        db.add(parent2_db)
        db.commit()
        db.refresh(parent1_db)
        db.refresh(parent2_db)

        # 子プロフィール作成
        child_profile_db = db_models.Profile(
            name="Child Shared",
            role="child",
            avatar_url=None,
            created_at=now,
            updated_at=now,
        )
        db.add(child_profile_db)
        db.commit()
        db.refresh(child_profile_db)

        # 親子関係を2つ作成
        relationship1 = db_models.FamilyRelationship(
            parent_id=parent1_db.id,
            child_id=child_profile_db.id,
            relationship_type="parent",
            created_at=now,
        )
        relationship2 = db_models.FamilyRelationship(
            parent_id=parent2_db.id,
            child_id=child_profile_db.id,
            relationship_type="parent",
            created_at=now,
        )
        db.add(relationship1)
        db.add(relationship2)
        db.commit()

        # Act & Assert: 両親に対して has_relationship が true を返す
        assert profile_service.family_relationship_repo.has_relationship(
            str(parent1_db.id), str(child_profile_db.id)
        )
        assert profile_service.family_relationship_repo.has_relationship(
            str(parent2_db.id), str(child_profile_db.id)
        )

        # 無関係の親に対しては false
        unrelated_parent = db_models.Profile(
            name="Unrelated",
            role="parent",
            avatar_url=None,
            created_at=now,
            updated_at=now,
        )
        db.add(unrelated_parent)
        db.commit()
        db.refresh(unrelated_parent)

        assert not profile_service.family_relationship_repo.has_relationship(
            str(unrelated_parent.id), str(child_profile_db.id)
        )

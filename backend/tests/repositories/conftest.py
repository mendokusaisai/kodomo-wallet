import uuid
from datetime import UTC, datetime

import pytest

from app.repositories.sqlalchemy.models import Account, Profile


@pytest.fixture
def sample_profile() -> Profile:
    """テスト用のサンプルプロフィールを作成"""
    now = datetime.now(UTC)
    return Profile(
        id=uuid.uuid4(),
        name="Test User",
        role="parent",
        avatar_url=None,
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def sample_account(sample_profile: Profile) -> Account:
    """テスト用のサンプルアカウントを作成"""
    return Account(
        id=uuid.uuid4(),
        user_id=sample_profile.id,
        balance=10000,
        currency="JPY",
        goal_name=None,
        goal_amount=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

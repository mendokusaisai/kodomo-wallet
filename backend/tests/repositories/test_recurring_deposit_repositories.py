"""RecurringDepositRepository の Firestore Emulator テスト"""

from datetime import UTC, datetime, timedelta

import pytest

from app.repositories.firestore.family_repository import FirestoreFamilyRepository
from app.repositories.firestore.account_repository import FirestoreAccountRepository
from app.repositories.firestore.recurring_deposit_repository import (
    FirestoreRecurringDepositRepository,
)


@pytest.fixture(autouse=True)
def cleanup_firestore():
    from app.core.database import get_firestore_client
    yield
    db = get_firestore_client()
    for doc in db.collection("families").stream():
        doc.reference.delete()
    for doc in db.collection("recurringDeposits").stream():
        doc.reference.delete()


@pytest.fixture
def family():
    return FirestoreFamilyRepository().create(name="テスト家族")


@pytest.fixture
def account(family):
    return FirestoreAccountRepository().create(family_id=family.id, name="テスト口座")


class TestFirestoreRecurringDepositRepository:
    def test_create_and_get_recurring_deposit(self, family, account):
        repo = FirestoreRecurringDepositRepository()
        now = datetime.now(UTC)
        next_at = now + timedelta(days=7)

        rd = repo.create(
            family_id=family.id,
            account_id=account.id,
            amount=1000,
            interval_days=7,
            next_execute_at=next_at,
            created_by_uid="parent-uid",
            created_at=now,
        )
        assert rd.id
        assert rd.amount == 1000
        assert rd.interval_days == 7

        fetched = repo.get_by_id(rd.id)
        assert fetched is not None
        assert fetched.id == rd.id

    def test_get_by_account_id(self, family, account):
        repo = FirestoreRecurringDepositRepository()
        now = datetime.now(UTC)
        repo.create(
            family_id=family.id,
            account_id=account.id,
            amount=500,
            interval_days=30,
            next_execute_at=now + timedelta(days=30),
            created_by_uid="parent-uid",
            created_at=now,
        )

        result = repo.get_by_account_id(family.id, account.id)
        assert result is not None
        assert result.amount == 500

    def test_get_by_account_id_not_found(self, family):
        repo = FirestoreRecurringDepositRepository()
        result = repo.get_by_account_id(family.id, "non-existent-account")
        assert result is None

    def test_get_due(self, family, account):
        repo = FirestoreRecurringDepositRepository()
        now = datetime.now(UTC)

        # 期限が過ぎているもの
        repo.create(
            family_id=family.id,
            account_id=account.id,
            amount=1000,
            interval_days=7,
            next_execute_at=now - timedelta(hours=1),
            created_by_uid="parent-uid",
            created_at=now,
        )

        due = repo.get_due(now)
        assert len(due) >= 1

    def test_delete_recurring_deposit(self, family, account):
        repo = FirestoreRecurringDepositRepository()
        now = datetime.now(UTC)
        rd = repo.create(
            family_id=family.id,
            account_id=account.id,
            amount=1000,
            interval_days=7,
            next_execute_at=now + timedelta(days=7),
            created_by_uid="parent-uid",
            created_at=now,
        )

        deleted = repo.delete(rd.id)
        assert deleted is True

        result = repo.get_by_id(rd.id)
        assert result is None

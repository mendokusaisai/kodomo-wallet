"""AccountRepository + TransactionRepository の Firestore Emulator テスト"""

import pytest

from app.repositories.firestore.account_repository import FirestoreAccountRepository
from app.repositories.firestore.family_repository import FirestoreFamilyRepository
from app.repositories.firestore.transaction_repository import FirestoreTransactionRepository
from datetime import UTC, datetime


FAMILY_ID = "test-family-tx"


@pytest.fixture(autouse=True)
def cleanup_firestore():
    from app.core.database import get_firestore_client
    yield
    db = get_firestore_client()
    for doc in db.collection("families").stream():
        doc.reference.delete()


@pytest.fixture
def family():
    repo = FirestoreFamilyRepository()
    return repo.create(name="テスト家族")


@pytest.fixture
def account(family):
    repo = FirestoreAccountRepository()
    return repo.create(family_id=family.id, name="テスト口座", balance=10000)


class TestFirestoreAccountRepository:
    def test_create_and_get_account(self, family):
        repo = FirestoreAccountRepository()
        account = repo.create(family_id=family.id, name="貯金口座")
        assert account.id
        assert account.family_id == family.id
        assert account.name == "貯金口座"
        assert account.balance == 0

        fetched = repo.get_by_id(family.id, account.id)
        assert fetched is not None
        assert fetched.id == account.id

    def test_get_by_family_id(self, family):
        repo = FirestoreAccountRepository()
        repo.create(family_id=family.id, name="口座1")
        repo.create(family_id=family.id, name="口座2")

        accounts = repo.get_by_family_id(family.id)
        assert len(accounts) == 2

    def test_get_by_id_not_found(self, family):
        repo = FirestoreAccountRepository()
        result = repo.get_by_id(family.id, "non-existent")
        assert result is None

    def test_update_balance(self, family, account):
        repo = FirestoreAccountRepository()
        repo.update_balance(account, 20000)

        fetched = repo.get_by_id(family.id, account.id)
        assert fetched is not None
        assert fetched.balance == 20000

    def test_delete_account(self, family, account):
        repo = FirestoreAccountRepository()
        deleted = repo.delete(family.id, account.id)
        assert deleted is True

        result = repo.get_by_id(family.id, account.id)
        assert result is None

    def test_delete_account_not_found(self, family):
        repo = FirestoreAccountRepository()
        result = repo.delete(family.id, "non-existent")
        assert result is False


class TestFirestoreTransactionRepository:
    def test_create_and_get_transaction(self, family, account):
        repo = FirestoreTransactionRepository()
        now = datetime.now(UTC)
        tx = repo.create(
            family_id=family.id,
            account_id=account.id,
            transaction_type="deposit",
            amount=1000,
            note="テスト入金",
            created_by_uid="parent-uid",
            created_at=now,
        )
        assert tx.id
        assert tx.amount == 1000
        assert tx.type == "deposit"

        txs = repo.get_by_account_id(family.id, account.id)
        assert len(txs) == 1
        assert txs[0].id == tx.id

    def test_get_by_account_id_with_limit(self, family, account):
        repo = FirestoreTransactionRepository()
        now = datetime.now(UTC)
        for i in range(5):
            repo.create(
                family_id=family.id,
                account_id=account.id,
                transaction_type="deposit",
                amount=1000 * (i + 1),
                note=f"入金 {i+1}",
                created_by_uid="parent-uid",
                created_at=now,
            )

        txs = repo.get_by_account_id(family.id, account.id, limit=3)
        assert len(txs) == 3

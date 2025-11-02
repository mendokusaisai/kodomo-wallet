"""GraphQL test fixtures"""

from collections.abc import Generator

import pytest
from injector import Injector
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.container import create_injector
from app.core.database import Base
from app.services import (
    AccountService,
    ProfileService,
    RecurringDepositService,
    TransactionService,
    WithdrawalRequestService,
)


@pytest.fixture
def in_memory_db() -> Generator[Session]:
    """テスト用のインメモリ SQLite データベースを作成"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def test_injector(in_memory_db: Session) -> Injector:
    """テスト用の依存性注入コンテナを作成"""
    return create_injector(in_memory_db)


@pytest.fixture
def graphql_context(
    in_memory_db: Session,
    test_injector: Injector,
) -> dict:
    """GraphQL コンテキストを作成（リクエストごとに利用されるコンテキスト）"""
    return {
        "db": in_memory_db,
        "profile_service": test_injector.get(ProfileService),
        "account_service": test_injector.get(AccountService),
        "transaction_service": test_injector.get(TransactionService),
        "withdrawal_request_service": test_injector.get(WithdrawalRequestService),
        "recurring_deposit_service": test_injector.get(RecurringDepositService),
    }

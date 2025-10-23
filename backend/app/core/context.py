"""
GraphQL context management.

Provides a context manager class for handling GraphQL request context,
including database session lifecycle and service injection.
"""

from __future__ import annotations

from typing import Any

from injector import Injector
from sqlalchemy.orm import Session

from app.core.container import create_injector
from app.core.database import SessionLocal
from app.services.business_services import (
    AccountService,
    ProfileService,
    TransactionService,
)


class GraphQLContext:
    """
    Context manager for GraphQL requests.

    Manages the lifecycle of database sessions and injected services.
    Ensures proper resource cleanup even when errors occur.

    Attributes:
        db: SQLAlchemy database session
        profile_service: Injected ProfileService instance
        account_service: Injected AccountService instance
        transaction_service: Injected TransactionService instance
    """

    def __init__(self) -> None:
        """Initialize the context (resources are created on enter)."""
        self._db: Session | None = None
        self._injector: Injector | None = None
        self.profile_service: ProfileService | None = None
        self.account_service: AccountService | None = None
        self.transaction_service: TransactionService | None = None

    @property
    def db(self) -> Session:
        """Get the database session (raises if not initialized)."""
        if self._db is None:
            raise RuntimeError("Database session not initialized. Use context manager.")
        return self._db

    def __enter__(self) -> GraphQLContext:
        """
        Enter the context manager.

        Creates database session and initializes services.

        Returns:
            GraphQLContext: Initialized context with all resources
        """
        self._db = SessionLocal()
        self._injector = create_injector(self._db)

        # Inject services
        self.profile_service = self._injector.get(ProfileService)
        self.account_service = self._injector.get(AccountService)
        self.transaction_service = self._injector.get(TransactionService)

        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        Exit the context manager.

        Commits the transaction if no exception occurred, otherwise rolls back.
        Ensures database session is properly closed in all cases.

        Args:
            exc_type: Exception type (if any)
            exc_val: Exception value (if any)
            exc_tb: Exception traceback (if any)
        """
        if self._db is not None:
            try:
                if exc_type is None:
                    # No exception: commit the transaction
                    self._db.commit()
                else:
                    # Exception occurred: rollback the transaction
                    self._db.rollback()
            finally:
                self._db.close()
                self._db = None
        self._injector = None
        self.profile_service = None
        self.account_service = None
        self.transaction_service = None

    async def __aenter__(self) -> GraphQLContext:
        """
        Async enter for compatibility with async contexts.

        Returns:
            GraphQLContext: Initialized context
        """
        return self.__enter__()

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        Async exit for compatibility with async contexts.

        Args:
            exc_type: Exception type (if any)
            exc_val: Exception value (if any)
            exc_tb: Exception traceback (if any)
        """
        self.__exit__(exc_type, exc_val, exc_tb)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert context to dictionary for GraphQL.

        Returns:
            dict: Context as dictionary with db and services
        """
        return {
            "db": self.db,
            "profile_service": self.profile_service,
            "account_service": self.account_service,
            "transaction_service": self.transaction_service,
        }

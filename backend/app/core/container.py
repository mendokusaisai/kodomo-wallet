"""
Dependency injection container using the 'injector' package.

This provides a cleaner, more maintainable DI implementation with:
- Automatic dependency resolution
- Type-safe bindings
- Scope management (Singleton, Request-scoped, etc.)
- Easy testing with Module overrides
"""

from injector import Binder, Injector, Module, singleton
from sqlalchemy.orm import Session

from app.repositories.interfaces import (
    AccountRepository,
    ProfileRepository,
    RecurringDepositRepository,
    TransactionRepository,
    WithdrawalRequestRepository,
)
from app.repositories.sqlalchemy_repositories import (
    SQLAlchemyAccountRepository,
    SQLAlchemyProfileRepository,
    SQLAlchemyRecurringDepositRepository,
    SQLAlchemyTransactionRepository,
    SQLAlchemyWithdrawalRequestRepository,
)
from app.services.business_services import (
    AccountService,
    ProfileService,
    RecurringDepositService,
    TransactionService,
    WithdrawalRequestService,
)


class RepositoryModule(Module):
    """
    Module that configures Repository bindings.

    This module binds Repository interfaces to their SQLAlchemy implementations.
    """

    def __init__(self, db: Session):
        self.db = db

    def configure(self, binder: Binder) -> None:
        """Configure repository bindings"""
        # Bind Repository interfaces to SQLAlchemy implementations
        # Each repository gets the same database session
        binder.bind(
            ProfileRepository,
            to=SQLAlchemyProfileRepository(self.db),
            scope=singleton,
        )
        binder.bind(
            AccountRepository,
            to=SQLAlchemyAccountRepository(self.db),
            scope=singleton,
        )
        binder.bind(
            TransactionRepository,
            to=SQLAlchemyTransactionRepository(self.db),
            scope=singleton,
        )
        binder.bind(
            WithdrawalRequestRepository,
            to=SQLAlchemyWithdrawalRequestRepository(self.db),
            scope=singleton,
        )
        binder.bind(
            RecurringDepositRepository,
            to=SQLAlchemyRecurringDepositRepository(self.db),
            scope=singleton,
        )


class ServiceModule(Module):
    """
    Module that configures Service bindings.

    Services are automatically injected with their repository dependencies.
    """

    def configure(self, binder: Binder) -> None:
        """Configure service bindings"""
        # Services will automatically receive their repository dependencies
        binder.bind(ProfileService, scope=singleton)
        binder.bind(AccountService, scope=singleton)
        binder.bind(TransactionService, scope=singleton)
        binder.bind(WithdrawalRequestService, scope=singleton)
        binder.bind(RecurringDepositService, scope=singleton)


def create_injector(db: Session) -> Injector:
    """
    Create a configured Injector instance.

    Args:
        db: SQLAlchemy database session

    Returns:
        Configured Injector instance

    Example:
        >>> from app.core.database import get_db
        >>> db = next(get_db())
        >>> injector = create_injector(db)
        >>> profile_service = injector.get(ProfileService)
    """
    return Injector([RepositoryModule(db), ServiceModule()])


# Convenience functions for backward compatibility
def get_profile_service(db: Session) -> ProfileService:
    """Get ProfileService instance with injected dependencies"""
    injector = create_injector(db)
    return injector.get(ProfileService)


def get_account_service(db: Session) -> AccountService:
    """Get AccountService instance with injected dependencies"""
    injector = create_injector(db)
    return injector.get(AccountService)


def get_transaction_service(db: Session) -> TransactionService:
    """Get TransactionService instance with injected dependencies"""
    injector = create_injector(db)
    return injector.get(TransactionService)


def get_withdrawal_request_service(db: Session) -> WithdrawalRequestService:
    """Get WithdrawalRequestService instance with injected dependencies"""
    injector = create_injector(db)
    return injector.get(WithdrawalRequestService)


def get_recurring_deposit_service(db: Session) -> RecurringDepositService:
    """Get RecurringDepositService instance with injected dependencies"""
    injector = create_injector(db)
    return injector.get(RecurringDepositService)

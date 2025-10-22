"""
GraphQL resolvers for queries and mutations.
"""

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.api.graphql.types import Account, Profile, Transaction
from app.models.models import Account as AccountModel
from app.models.models import Profile as ProfileModel
from app.models.models import Transaction as TransactionModel


def get_profile_by_id(db: Session, user_id: str) -> Profile | None:
    """Get user profile by ID"""
    profile = db.query(ProfileModel).filter(ProfileModel.id == user_id).first()
    if not profile:
        return None

    return profile


def get_accounts_by_user_id(db: Session, user_id: str) -> list[Account]:
    """Get all accounts for a user"""
    accounts = db.query(AccountModel).filter(AccountModel.user_id == user_id).all()
    return list(accounts)


def get_transactions_by_account_id(
    db: Session, account_id: str, limit: int = 50
) -> list[Transaction]:
    """Get transactions for an account"""
    transactions = (
        db.query(TransactionModel)
        .filter(TransactionModel.account_id == account_id)
        .order_by(TransactionModel.created_at.desc())
        .limit(limit)
        .all()
    )
    return list(transactions)


def create_deposit(
    db: Session, account_id: str, amount: int, description: str | None = None
) -> Transaction:
    """Create a deposit transaction"""
    # Get account
    account = db.query(AccountModel).filter(AccountModel.id == account_id).first()
    if not account:
        raise ValueError("Account not found")

    # Update balance
    account.balance += amount

    # Create transaction
    transaction = TransactionModel(
        account_id=account_id,
        type="deposit",
        amount=amount,
        description=description,
        created_at=datetime.now(UTC),
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction

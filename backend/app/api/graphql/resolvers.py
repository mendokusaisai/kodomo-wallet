"""
GraphQL resolvers for queries and mutations.
"""

from datetime import datetime
from typing import List, Optional

from app.api.graphql.types import Account, Profile, Transaction
from app.models.models import Account as AccountModel
from app.models.models import Profile as ProfileModel
from app.models.models import Transaction as TransactionModel
from sqlalchemy.orm import Session


def get_profile_by_id(db: Session, user_id: str) -> Optional[Profile]:
    """Get user profile by ID"""
    profile = db.query(ProfileModel).filter(ProfileModel.id == user_id).first()
    if not profile:
        return None

    return Profile(
        id=str(profile.id),
        name=profile.name,
        role=profile.role,
        avatar_url=profile.avatar_url,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


def get_accounts_by_user_id(db: Session, user_id: str) -> List[Account]:
    """Get all accounts for a user"""
    accounts = db.query(AccountModel).filter(AccountModel.user_id == user_id).all()

    return [
        Account(
            id=str(account.id),
            user_id=str(account.user_id),
            balance=account.balance,
            currency=account.currency,
            goal_name=account.goal_name,
            goal_amount=account.goal_amount,
            created_at=account.created_at,
            updated_at=account.updated_at,
        )
        for account in accounts
    ]


def get_transactions_by_account_id(
    db: Session, account_id: str, limit: int = 50
) -> List[Transaction]:
    """Get transactions for an account"""
    transactions = (
        db.query(TransactionModel)
        .filter(TransactionModel.account_id == account_id)
        .order_by(TransactionModel.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        Transaction(
            id=str(tx.id),
            account_id=str(tx.account_id),
            type=tx.type,
            amount=tx.amount,
            description=tx.description,
            created_at=tx.created_at,
        )
        for tx in transactions
    ]


def create_deposit(
    db: Session, account_id: str, amount: int, description: Optional[str] = None
) -> Transaction:
    """Create a deposit transaction"""
    # Get account
    account = db.query(AccountModel).filter(AccountModel.id == account_id).first()
    if not account:
        raise ValueError("Account not found")

    # Update balance
    account.balance += amount
    account.updated_at = datetime.utcnow().isoformat()

    # Create transaction
    transaction = TransactionModel(
        account_id=account_id,
        type="deposit",
        amount=amount,
        description=description,
        created_at=datetime.utcnow().isoformat(),
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return Transaction(
        id=str(transaction.id),
        account_id=str(transaction.account_id),
        type=transaction.type,
        amount=transaction.amount,
        description=transaction.description,
        created_at=transaction.created_at,
    )

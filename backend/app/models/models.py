"""
SQLAlchemy models for the application.
"""

import uuid

from app.core.database import Base
from sqlalchemy import BigInteger, CheckConstraint, Column, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Profile(Base):
    """User profile model"""

    __tablename__ = "profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    role = Column(Text, nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=True)
    avatar_url = Column(Text, nullable=True)
    created_at = Column(Text, nullable=False)
    updated_at = Column(Text, nullable=False)

    # Relationships
    accounts = relationship(
        "Account", back_populates="user", cascade="all, delete-orphan"
    )
    children = relationship("Profile", backref="parent", remote_side=[id])

    __table_args__ = (
        CheckConstraint("role IN ('parent', 'child')", name="check_role"),
    )


class Account(Base):
    """Account model"""

    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    balance = Column(BigInteger, default=0, nullable=False)
    currency = Column(Text, default="JPY", nullable=False)
    goal_name = Column(Text, nullable=True)
    goal_amount = Column(BigInteger, nullable=True)
    created_at = Column(Text, nullable=False)
    updated_at = Column(Text, nullable=False)

    # Relationships
    user = relationship("Profile", back_populates="accounts")
    transactions = relationship(
        "Transaction", back_populates="account", cascade="all, delete-orphan"
    )
    withdrawal_requests = relationship(
        "WithdrawalRequest", back_populates="account", cascade="all, delete-orphan"
    )


class Transaction(Base):
    """Transaction model"""

    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    type = Column(Text, nullable=False)
    amount = Column(BigInteger, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(Text, nullable=False)

    # Relationships
    account = relationship("Account", back_populates="transactions")

    __table_args__ = (
        CheckConstraint(
            "type IN ('deposit', 'withdraw', 'reward')", name="check_transaction_type"
        ),
    )


class WithdrawalRequest(Base):
    """Withdrawal request model"""

    __tablename__ = "withdrawal_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    amount = Column(BigInteger, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Text, default="pending", nullable=False)
    created_at = Column(Text, nullable=False)
    updated_at = Column(Text, nullable=False)

    # Relationships
    account = relationship("Account", back_populates="withdrawal_requests")

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'approved', 'rejected')", name="check_status"
        ),
    )

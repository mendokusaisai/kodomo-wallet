"""
SQLAlchemy データベースモデル（インフラ層）
"""

import uuid

from sqlalchemy import BigInteger, CheckConstraint, Column, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Profile(Base):
    """ユーザープロフィールモデル"""

    __tablename__ = "profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    auth_user_id = Column(UUID(as_uuid=True), nullable=True)
    name = Column(Text, nullable=False)
    role = Column(Text, nullable=False)
    avatar_url = Column(Text, nullable=True)
    # DBは timestamptz を使用しているため DateTime(timezone=True) を使用
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)

    # リレーション
    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    # family relationships
    parent_relationships = relationship(
        "FamilyRelationship",
        foreign_keys="FamilyRelationship.child_id",
        back_populates="child",
        cascade="all, delete-orphan",
    )
    child_relationships = relationship(
        "FamilyRelationship",
        foreign_keys="FamilyRelationship.parent_id",
        back_populates="parent",
        cascade="all, delete-orphan",
    )

    __table_args__ = (CheckConstraint("role IN ('parent', 'child')", name="check_role"),)


class Account(Base):
    """アカウントモデル"""

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

    # リレーション
    user = relationship("Profile", back_populates="accounts")
    transactions = relationship(
        "Transaction", back_populates="account", cascade="all, delete-orphan"
    )
    withdrawal_requests = relationship(
        "WithdrawalRequest", back_populates="account", cascade="all, delete-orphan"
    )
    recurring_deposits = relationship(
        "RecurringDeposit", back_populates="account", cascade="all, delete-orphan"
    )


class Transaction(Base):
    """トランザクションモデル"""

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

    # リレーション
    account = relationship("Account", back_populates="transactions")

    __table_args__ = (
        CheckConstraint("type IN ('deposit', 'withdraw', 'reward')", name="check_transaction_type"),
    )


class WithdrawalRequest(Base):
    """出金リクエストモデル"""

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

    # リレーション
    account = relationship("Account", back_populates="withdrawal_requests")

    __table_args__ = (
        CheckConstraint("status IN ('pending', 'approved', 'rejected')", name="check_status"),
    )


class FamilyRelationship(Base):
    """家族関係モデル（親-子の多対多）"""

    __tablename__ = "family_relationships"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_id = Column(
        UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False
    )
    child_id = Column(
        UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False
    )
    relationship_type = Column(Text, default="parent", nullable=False)
    created_at = Column(Text, nullable=False)

    parent = relationship("Profile", foreign_keys=[parent_id], back_populates="child_relationships")
    child = relationship("Profile", foreign_keys=[child_id], back_populates="parent_relationships")


class RecurringDeposit(Base):
    """定期入金モデル（自動お小遣い）"""

    __tablename__ = "recurring_deposits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    amount = Column(BigInteger, nullable=False)
    day_of_month = Column(BigInteger, nullable=False)
    is_active = Column(Text, default="true", nullable=False)
    created_at = Column(Text, nullable=False)
    updated_at = Column(Text, nullable=False)

    # リレーション
    account = relationship("Account", back_populates="recurring_deposits")

    __table_args__ = (
        CheckConstraint("amount > 0", name="check_amount_positive"),
        CheckConstraint(
            "day_of_month >= 1 AND day_of_month <= 31", name="check_day_of_month_range"
        ),
    )


class ParentInvite(Base):
    """親招待モデル（メール/リンクによる親追加のための招待）"""

    __tablename__ = "parent_invites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token = Column(UUID(as_uuid=True), nullable=False, unique=True, default=uuid.uuid4)
    child_id = Column(
        UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False
    )
    inviter_id = Column(
        UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False
    )
    email = Column(Text, nullable=False)
    status = Column(Text, nullable=False, default="pending")  # pending/accepted/expired/cancelled
    expires_at = Column(Text, nullable=False)
    created_at = Column(Text, nullable=False)


class ChildInvite(Base):
    """子どもの認証アカウント作成招待モデル"""

    __tablename__ = "child_invites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token = Column(UUID(as_uuid=True), nullable=False, unique=True, default=uuid.uuid4)
    child_id = Column(
        UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False
    )
    email = Column(Text, nullable=False)
    status = Column(Text, nullable=False, default="pending")  # pending/accepted/expired/cancelled
    expires_at = Column(Text, nullable=False)
    created_at = Column(Text, nullable=False)

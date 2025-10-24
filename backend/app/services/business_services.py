"""
Business logic services.

These services contain the business logic and use repositories for data access.
"""

from datetime import UTC, datetime

from injector import inject

from app.core.exceptions import InvalidAmountException, ResourceNotFoundException
from app.models.models import Account, Profile, Transaction
from app.repositories.interfaces import (
    AccountRepository,
    ProfileRepository,
    TransactionRepository,
)


class ProfileService:
    """Service for profile-related business logic"""

    @inject
    def __init__(
        self, profile_repo: ProfileRepository, account_repo: AccountRepository
    ):
        self.profile_repo = profile_repo
        self.account_repo = account_repo

    def get_profile(self, user_id: str) -> Profile | None:
        """Get user profile by ID"""
        return self.profile_repo.get_by_id(user_id)

    def get_children(self, parent_id: str) -> list[Profile]:
        """Get all children for a parent"""
        return self.profile_repo.get_children(parent_id)

    def get_by_auth_user_id(self, auth_user_id: str) -> Profile | None:
        """Get profile by auth user ID"""
        return self.profile_repo.get_by_auth_user_id(auth_user_id)

    def create_child(
        self, parent_id: str, child_name: str, initial_balance: int = 0, email: str | None = None
    ) -> Profile:
        """Create a child profile without authentication and their account"""
        # 親が存在するか確認
        parent = self.profile_repo.get_by_id(parent_id)
        if not parent or parent.role != "parent":
            raise ResourceNotFoundException("Parent", parent_id)

        # 子どもプロフィール作成
        child_profile = self.profile_repo.create_child(child_name, parent_id, email)

        # 子どものアカウント作成
        self.account_repo.create(
            user_id=str(child_profile.id), balance=initial_balance, currency="JPY"
        )

        return child_profile

    def link_child_to_auth(self, child_id: str, auth_user_id: str) -> Profile:
        """Link child profile to authentication account"""
        # 子どもプロフィールが存在するか確認
        child = self.profile_repo.get_by_id(child_id)
        if not child or child.role != "child":
            raise ResourceNotFoundException("Child", child_id)

        # 認証アカウントに既に紐づいているプロフィールがないか確認
        existing_profile = self.profile_repo.get_by_auth_user_id(auth_user_id)
        if existing_profile:
            raise InvalidAmountException(
                0, f"Auth account already linked to profile {existing_profile.id}"
            )

        return self.profile_repo.link_to_auth(child_id, auth_user_id)

    def link_child_to_auth_by_email(self, child_id: str, email: str) -> Profile:
        """Link child profile to authentication account by email"""
        # Supabase auth.users テーブルからメールアドレスで認証アカウントを検索
        # Note: この実装はSupabaseの直接アクセスが必要
        # 簡略化のため、auth_user_idを取得する処理を追加
        from sqlalchemy import text

        from app.core.database import get_db

        db = next(get_db())

        # auth.users からメールアドレスで検索
        result = db.execute(
            text("SELECT id FROM auth.users WHERE email = :email"), {"email": email}
        ).fetchone()

        if not result:
            raise ResourceNotFoundException("Auth user", email)

        auth_user_id = str(result[0])
        return self.link_child_to_auth(child_id, auth_user_id)

    def auto_link_on_signup(self, auth_user_id: str, email: str) -> Profile | None:
        """Automatically link unauthenticated child profile on signup if email matches"""
        # メールアドレスで未認証子どもプロフィールを検索
        child_profile = self.profile_repo.get_by_email(email)

        if child_profile:
            # 自動的に紐付け
            return self.profile_repo.link_to_auth(str(child_profile.id), auth_user_id)

        return None

    def invite_child_to_auth(self, child_id: str, email: str) -> Profile:
        """Invite child to create auth account and link profile"""
        import os

        import httpx

        supabase_url = os.getenv("SUPABASE_URL")
        supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if not supabase_url or not supabase_service_key:
            raise ValueError("Supabase configuration not found")

        # 子どもプロフィールが存在するか確認
        child = self.profile_repo.get_by_id(child_id)
        if not child or child.role != "child":
            raise ResourceNotFoundException("Child", child_id)

        # プロフィールにメールアドレスを保存
        child.email = email
        child.updated_at = str(datetime.now(UTC))

        # Supabase Management API で招待メール送信（httpx使用）
        try:
            response = httpx.post(
                f"{supabase_url}/auth/v1/invite",
                headers={
                    "apikey": supabase_service_key,
                    "Authorization": f"Bearer {supabase_service_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "email": email,
                    "data": {
                        "child_profile_id": child_id,
                        "name": child.name,
                        "role": "child",  # 招待経由は必ず子どもロール
                    },
                },
                timeout=10.0,
            )
            response.raise_for_status()
            return child
        except httpx.HTTPError as e:
            raise InvalidAmountException(0, f"Failed to send invitation: {str(e)}") from e


class AccountService:
    """Service for account-related business logic"""

    @inject
    def __init__(
        self, account_repo: AccountRepository, profile_repo: ProfileRepository
    ):
        self.account_repo = account_repo
        self.profile_repo = profile_repo

    def get_user_accounts(self, user_id: str) -> list[Account]:
        """Get all accounts for a user"""
        return self.account_repo.get_by_user_id(user_id)

    def get_family_accounts(self, user_id: str) -> list[Account]:
        """Get accounts for user. If parent, only return children's accounts"""
        # Get user profile to check role
        profile = self.profile_repo.get_by_id(user_id)

        if profile and profile.role == "parent":
            # Parents only see their children's accounts, not their own
            accounts = []
            children = self.profile_repo.get_children(user_id)
            for child in children:
                child_accounts = self.account_repo.get_by_user_id(str(child.id))
                accounts.extend(child_accounts)
        else:
            # Children see their own accounts
            accounts = self.account_repo.get_by_user_id(user_id)

        return accounts


class TransactionService:
    """Service for transaction-related business logic"""

    @inject
    def __init__(
        self,
        transaction_repo: TransactionRepository,
        account_repo: AccountRepository,
    ):
        self.transaction_repo = transaction_repo
        self.account_repo = account_repo

    def get_account_transactions(self, account_id: str, limit: int = 50) -> list[Transaction]:
        """Get transactions for an account"""
        return self.transaction_repo.get_by_account_id(account_id, limit)

    def create_deposit(
        self, account_id: str, amount: int, description: str | None = None
    ) -> Transaction:
        """Create a deposit transaction and update account balance"""
        # Validate amount
        if amount <= 0:
            raise InvalidAmountException(amount, "Amount must be greater than zero")

        # Get account
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ResourceNotFoundException("Account", account_id)

        # Update balance (type: ignore for SQLAlchemy Column type)
        new_balance = int(account.balance) + amount  # type: ignore[arg-type]
        self.account_repo.update_balance(account, new_balance)

        # Create transaction
        transaction = self.transaction_repo.create(
            account_id=account_id,
            transaction_type="deposit",
            amount=amount,
            description=description,
            created_at=datetime.now(UTC),
        )

        return transaction

    def create_withdraw(
        self, account_id: str, amount: int, description: str | None = None
    ) -> Transaction:
        """Create a withdraw transaction and update account balance"""
        # Validate amount
        if amount <= 0:
            raise InvalidAmountException(amount, "Amount must be greater than zero")

        # Get account
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ResourceNotFoundException("Account", account_id)

        # Check if balance is sufficient
        current_balance = int(account.balance)  # type: ignore[arg-type]
        if current_balance < amount:
            raise InvalidAmountException(
                amount, f"Insufficient balance. Current: {current_balance}, Required: {amount}"
            )

        # Update balance
        new_balance = current_balance - amount
        self.account_repo.update_balance(account, new_balance)

        # Create transaction
        transaction = self.transaction_repo.create(
            account_id=account_id,
            transaction_type="withdraw",
            amount=amount,
            description=description,
            created_at=datetime.now(UTC),
        )

        return transaction

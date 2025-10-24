"""
Business logic services.

These services contain the business logic and use repositories for data access.
"""

from datetime import UTC, datetime

from injector import inject

from app.core.exceptions import InvalidAmountException, ResourceNotFoundException
from app.models.models import Account, Profile, RecurringDeposit, Transaction, WithdrawalRequest
from app.repositories.interfaces import (
    AccountRepository,
    ProfileRepository,
    RecurringDepositRepository,
    TransactionRepository,
    WithdrawalRequestRepository,
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

    def update_profile(
        self,
        user_id: str,
        current_user_id: str,
        name: str | None = None,
        avatar_url: str | None = None,
    ) -> Profile:
        """Update user profile (self or parent can edit child)"""
        # Get target profile
        profile = self.profile_repo.get_by_id(user_id)
        if not profile:
            raise ResourceNotFoundException("Profile", user_id)

        # Get current user profile
        current_user = self.profile_repo.get_by_id(current_user_id)
        if not current_user:
            raise ResourceNotFoundException("Current user", current_user_id)

        # Check permissions: user can edit themselves or parent can edit their child
        if user_id != current_user_id:
            # Only parents can edit other profiles
            if str(current_user.role) != "parent":  # type: ignore
                raise InvalidAmountException(0, "You don't have permission to edit this profile")

            # Parent can only edit their own children
            if str(profile.role) != "child" or str(profile.parent_id) != current_user_id:  # type: ignore
                raise InvalidAmountException(
                    0, "You can only edit profiles of your own children"
                )

        # Update fields if provided
        if name is not None:
            profile.name = name  # type: ignore
        if avatar_url is not None:
            profile.avatar_url = avatar_url  # type: ignore

        profile.updated_at = str(datetime.now(UTC))  # type: ignore

        return profile

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

    def delete_child(self, parent_id: str, child_id: str) -> bool:
        """Delete a child profile and all associated data"""
        # 親が存在するか確認
        parent = self.profile_repo.get_by_id(parent_id)
        if not parent or parent.role != "parent":
            raise ResourceNotFoundException("Parent", parent_id)

        # 子どもが存在するか確認
        child = self.profile_repo.get_by_id(child_id)
        if not child or child.role != "child":
            raise ResourceNotFoundException("Child", child_id)

        # 子どもが実際にこの親のものか確認
        if str(child.parent_id) != parent_id:
            raise InvalidAmountException(0, "Child does not belong to this parent")

        # 子どもに紐づくアカウントを取得
        accounts = self.account_repo.get_by_user_id(child_id)

        # アカウントを削除（トランザクション、出金リクエストもカスケード削除される）
        for account in accounts:
            self.account_repo.delete(str(account.id))

        # プロフィールを削除
        self.profile_repo.delete(child_id)

        return True

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

    def update_goal(
        self, account_id: str, goal_name: str | None, goal_amount: int | None
    ) -> Account:
        """Update savings goal for an account"""
        # Get account
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ResourceNotFoundException("Account", account_id)

        # Validate goal amount if provided
        if goal_amount is not None and goal_amount < 0:
            raise InvalidAmountException(goal_amount, "Goal amount must be non-negative")

        # Update goal fields
        account.goal_name = goal_name  # type: ignore
        account.goal_amount = goal_amount  # type: ignore
        account.updated_at = str(datetime.now(UTC))  # type: ignore

        return account


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


class WithdrawalRequestService:
    """Service for withdrawal request business logic"""

    @inject
    def __init__(
        self,
        withdrawal_request_repo: WithdrawalRequestRepository,
        account_repo: AccountRepository,
        transaction_service: TransactionService,
    ):
        self.withdrawal_request_repo = withdrawal_request_repo
        self.account_repo = account_repo
        self.transaction_service = transaction_service

    def create_withdrawal_request(
        self, account_id: str, amount: int, description: str | None = None
    ) -> WithdrawalRequest:
        """Create a withdrawal request (child initiates)"""
        # Validate amount
        if amount <= 0:
            raise InvalidAmountException(amount, "Amount must be greater than zero")

        # Get account
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ResourceNotFoundException("Account", account_id)

        # Check if balance is sufficient (for informational purposes)
        current_balance = int(account.balance)  # type: ignore[arg-type]
        if current_balance < amount:
            raise InvalidAmountException(
                amount, f"Insufficient balance. Current: {current_balance}, Required: {amount}"
            )

        # Create withdrawal request
        request = self.withdrawal_request_repo.create(
            account_id=account_id,
            amount=amount,
            description=description,
            created_at=datetime.now(UTC),
        )

        return request

    def get_pending_requests_for_parent(self, parent_id: str) -> list[WithdrawalRequest]:
        """Get all pending withdrawal requests for a parent's children"""
        return self.withdrawal_request_repo.get_pending_by_parent(parent_id)

    def approve_withdrawal_request(self, request_id: str) -> WithdrawalRequest:
        """Approve a withdrawal request and create the withdraw transaction"""
        # Get request
        request = self.withdrawal_request_repo.get_by_id(request_id)
        if not request:
            raise ResourceNotFoundException("WithdrawalRequest", request_id)

        # Check if already processed
        if request.status != "pending":  # type: ignore[comparison-overlap]
            raise InvalidAmountException(0, f"Request already {request.status}")

        # Create withdraw transaction
        try:
            self.transaction_service.create_withdraw(
                account_id=str(request.account_id),
                amount=int(request.amount),  # type: ignore[arg-type]
                description=request.description,  # type: ignore[arg-type]
            )
        except Exception as e:
            # Update status to rejected if withdrawal fails
            self.withdrawal_request_repo.update_status(
                request, "rejected", datetime.now(UTC)
            )
            raise e

        # Update request status
        updated_request = self.withdrawal_request_repo.update_status(
            request, "approved", datetime.now(UTC)
        )

        return updated_request

    def reject_withdrawal_request(self, request_id: str) -> WithdrawalRequest:
        """Reject a withdrawal request"""
        # Get request
        request = self.withdrawal_request_repo.get_by_id(request_id)
        if not request:
            raise ResourceNotFoundException("WithdrawalRequest", request_id)

        # Check if already processed
        if request.status != "pending":  # type: ignore[comparison-overlap]
            raise InvalidAmountException(0, f"Request already {request.status}")

        # Update request status
        updated_request = self.withdrawal_request_repo.update_status(
            request, "rejected", datetime.now(UTC)
        )

        return updated_request


class RecurringDepositService:
    """Service for recurring deposit-related business logic"""

    @inject
    def __init__(
        self,
        recurring_deposit_repo: RecurringDepositRepository,
        account_repo: AccountRepository,
        profile_repo: ProfileRepository,
    ):
        self.recurring_deposit_repo = recurring_deposit_repo
        self.account_repo = account_repo
        self.profile_repo = profile_repo

    def get_recurring_deposit(
        self, account_id: str, current_user_id: str
    ) -> RecurringDeposit | None:
        """Get recurring deposit settings (parent only)"""
        # Get account
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ResourceNotFoundException("Account", account_id)

        # Get account owner's profile
        profile = self.profile_repo.get_by_id(str(account.user_id))
        if not profile:
            raise ResourceNotFoundException("Profile", str(account.user_id))

        # Only parent can view recurring deposit settings
        if str(profile.role) == "parent":
            # Parent viewing their own account (not typical, but allow it)
            if str(account.user_id) != current_user_id:
                raise InvalidAmountException(0, "You don't have permission to view this")
        elif str(profile.role) == "child":
            # Must be the parent of this child
            if str(profile.parent_id) != current_user_id:
                raise InvalidAmountException(
                    0, "You can only view recurring deposits for your own children"
                )
        else:
            raise InvalidAmountException(0, "Invalid role")

        return self.recurring_deposit_repo.get_by_account_id(account_id)

    def create_or_update_recurring_deposit(
        self,
        account_id: str,
        current_user_id: str,
        amount: int,
        day_of_month: int,
        is_active: bool = True,
    ) -> RecurringDeposit:
        """Create or update recurring deposit settings (parent only)"""
        # Validate amount
        if amount <= 0:
            raise InvalidAmountException(amount, "Amount must be positive")

        # Validate day of month
        if day_of_month < 1 or day_of_month > 31:
            raise InvalidAmountException(day_of_month, "Day must be between 1 and 31")

        # Get account
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ResourceNotFoundException("Account", account_id)

        # Get account owner's profile
        profile = self.profile_repo.get_by_id(str(account.user_id))
        if not profile:
            raise ResourceNotFoundException("Profile", str(account.user_id))

        # Only parent can modify recurring deposit settings
        if str(profile.role) == "parent":
            # Parent modifying their own account (not typical, but allow it)
            if str(account.user_id) != current_user_id:
                raise InvalidAmountException(0, "You don't have permission to modify this")
        elif str(profile.role) == "child":
            # Must be the parent of this child
            if str(profile.parent_id) != current_user_id:
                raise InvalidAmountException(
                    0, "You can only modify recurring deposits for your own children"
                )
        else:
            raise InvalidAmountException(0, "Invalid role")

        # Check if recurring deposit already exists
        existing = self.recurring_deposit_repo.get_by_account_id(account_id)

        now = datetime.now(UTC)

        if existing:
            # Update existing
            return self.recurring_deposit_repo.update(
                existing, amount, day_of_month, is_active, now
            )
        else:
            # Create new
            return self.recurring_deposit_repo.create(
                account_id, amount, day_of_month, now
            )

    def delete_recurring_deposit(
        self, account_id: str, current_user_id: str
    ) -> bool:
        """Delete recurring deposit settings (parent only)"""
        # Get account
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ResourceNotFoundException("Account", account_id)

        # Get account owner's profile
        profile = self.profile_repo.get_by_id(str(account.user_id))
        if not profile:
            raise ResourceNotFoundException("Profile", str(account.user_id))

        # Only parent can delete recurring deposit settings
        if str(profile.role) == "parent":
            # Parent deleting their own account (not typical, but allow it)
            if str(account.user_id) != current_user_id:
                raise InvalidAmountException(0, "You don't have permission to delete this")
        elif str(profile.role) == "child":
            # Must be the parent of this child
            if str(profile.parent_id) != current_user_id:
                raise InvalidAmountException(
                    0, "You can only delete recurring deposits for your own children"
                )
        else:
            raise InvalidAmountException(0, "Invalid role")

        # Get recurring deposit
        recurring_deposit = self.recurring_deposit_repo.get_by_account_id(account_id)
        if not recurring_deposit:
            raise ResourceNotFoundException("RecurringDeposit", account_id)

        return self.recurring_deposit_repo.delete(recurring_deposit)

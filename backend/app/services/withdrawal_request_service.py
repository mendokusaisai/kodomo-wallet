from datetime import UTC, datetime

from injector import inject

from app.core.exceptions import InvalidAmountException, ResourceNotFoundException
from app.models.models import WithdrawalRequest
from app.repositories.interfaces import AccountRepository, WithdrawalRequestRepository


class WithdrawalRequestService:
    """出金リクエストのビジネスロジックサービス"""

    @inject
    def __init__(
        self,
        withdrawal_request_repo: WithdrawalRequestRepository,
        account_repo: AccountRepository,
    ):
        self.withdrawal_request_repo = withdrawal_request_repo
        self.account_repo = account_repo

    def create_withdrawal_request(
        self, account_id: str, amount: int, description: str | None = None
    ) -> WithdrawalRequest:
        """出金リクエストを作成（子供が開始）"""
        # 金額を検証
        if amount <= 0:
            raise InvalidAmountException(amount, "Amount must be greater than zero")

        # アカウントを取得
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ResourceNotFoundException("Account", account_id)

        # 残高が十分か確認（情報提供のため）
        current_balance = int(account.balance)  # type: ignore[arg-type]
        if current_balance < amount:
            raise InvalidAmountException(
                amount, f"Insufficient balance. Current: {current_balance}, Required: {amount}"
            )

        # 出金リクエストを作成
        request = self.withdrawal_request_repo.create(
            account_id=account_id,
            amount=amount,
            description=description,
            created_at=datetime.now(UTC),
        )

        return request

    def get_pending_requests_for_parent(self, parent_id: str) -> list[WithdrawalRequest]:
        """親の子供の全ての保留中出金リクエストを取得"""
        return self.withdrawal_request_repo.get_pending_by_parent(parent_id)

    def approve_withdrawal_request(self, request_id: str, transaction_service) -> WithdrawalRequest:
        """出金リクエストを承認し出金トランザクションを作成"""
        # リクエストを取得
        request = self.withdrawal_request_repo.get_by_id(request_id)
        if not request:
            raise ResourceNotFoundException("WithdrawalRequest", request_id)

        # 既に処理済みか確認
        if request.status != "pending":  # type: ignore[comparison-overlap]
            raise InvalidAmountException(0, f"Request already {request.status}")

        # 出金トランザクションを作成
        try:
            transaction_service.create_withdraw(
                account_id=str(request.account_id),
                amount=int(request.amount),  # type: ignore[arg-type]
                description=request.description,  # type: ignore[arg-type]
            )
        except Exception as e:
            # 出金が失敗した場合はステータスを拒否に更新
            self.withdrawal_request_repo.update_status(request, "rejected", datetime.now(UTC))
            raise e

        # リクエストステータスを更新
        updated_request = self.withdrawal_request_repo.update_status(
            request, "approved", datetime.now(UTC)
        )

        return updated_request

    def reject_withdrawal_request(self, request_id: str) -> WithdrawalRequest:
        """出金リクエストを拒否"""
        # リクエストを取得
        request = self.withdrawal_request_repo.get_by_id(request_id)
        if not request:
            raise ResourceNotFoundException("WithdrawalRequest", request_id)

        # 既に処理済みか確認
        if request.status != "pending":  # type: ignore[comparison-overlap]
            raise InvalidAmountException(0, f"Request already {request.status}")

        # リクエストステータスを更新
        updated_request = self.withdrawal_request_repo.update_status(
            request, "rejected", datetime.now(UTC)
        )

        return updated_request

"""
ドメイン固有エラーのためのカスタム例外

これらの例外は、汎用的なPython例外を使用するよりも
優れたエラーハンドリングとより具体的なエラーメッセージを提供します。
"""

from typing import Any


class DomainException(Exception):
    """
    すべてのドメイン固有エラーの基底例外

    APIの境界でキャッチして適切なHTTP/GraphQLエラーレスポンスに変換する必要があります。
    """

    def __init__(self, message: str, code: str | None = None):
        self.message = message
        self.code = code or self.__class__.__name__
        super().__init__(self.message)


class ResourceNotFoundException(DomainException):
    """
    要求されたリソースが見つからない場合に発生します。

    例:
        - アカウントが見つからない
        - プロフィールが見つからない
        - トランザクションが見つからない
    """

    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} with ID '{resource_id}' not found"
        super().__init__(message, code="RESOURCE_NOT_FOUND")
        self.resource_type = resource_type
        self.resource_id = resource_id


class BusinessRuleViolationException(DomainException):
    """
    ビジネスルールに違反した場合に発生します。

    例:
        - 無効なトランザクション金額
        - 無効なアカウント状態
        - 操作に対する無効な権限
    """

    def __init__(self, rule: str, details: str | None = None):
        message = f"Business rule violation: {rule}"
        if details:
            message += f" - {details}"
        super().__init__(message, code="BUSINESS_RULE_VIOLATION")
        self.rule = rule
        self.details = details


class InsufficientBalanceException(DomainException):
    """
    アカウントの残高がトランザクションに対して不足している場合に発生します。
    """

    def __init__(self, account_id: str, required: int, available: int):
        message = (
            f"Insufficient balance in account '{account_id}': "
            f"required {required}, available {available}"
        )
        super().__init__(message, code="INSUFFICIENT_BALANCE")
        self.account_id = account_id
        self.required = required
        self.available = available


class InvalidAmountException(DomainException):
    """
    トランザクション金額が無効な場合に発生します。

    例:
        - 負の金額
        - ゼロの金額
        - 最大値を超える金額
    """

    def __init__(self, amount: int, reason: str):
        message = f"Invalid amount {amount}: {reason}"
        super().__init__(message, code="INVALID_AMOUNT")
        self.amount = amount
        self.reason = reason


class ValidationException(DomainException):
    """
    入力検証が失敗した場合に発生します。
    """

    def __init__(self, field: str, value: Any, reason: str):
        message = f"Validation failed for field '{field}': {reason}"
        super().__init__(message, code="VALIDATION_ERROR")
        self.field = field
        self.value = value
        self.reason = reason

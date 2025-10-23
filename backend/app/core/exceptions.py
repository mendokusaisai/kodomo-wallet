"""
Custom exceptions for domain-specific errors.

These exceptions provide better error handling and more specific error messages
than using generic Python exceptions.
"""

from typing import Any


class DomainException(Exception):
    """
    Base exception for all domain-specific errors.

    This should be caught at the API boundary to convert to appropriate
    HTTP/GraphQL error responses.
    """

    def __init__(self, message: str, code: str | None = None):
        self.message = message
        self.code = code or self.__class__.__name__
        super().__init__(self.message)


class ResourceNotFoundException(DomainException):
    """
    Raised when a requested resource is not found.

    Examples:
        - Account not found
        - Profile not found
        - Transaction not found
    """

    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} with ID '{resource_id}' not found"
        super().__init__(message, code="RESOURCE_NOT_FOUND")
        self.resource_type = resource_type
        self.resource_id = resource_id


class BusinessRuleViolationException(DomainException):
    """
    Raised when a business rule is violated.

    Examples:
        - Invalid transaction amount
        - Invalid account state
        - Invalid permission for operation
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
    Raised when an account has insufficient balance for a transaction.
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
    Raised when a transaction amount is invalid.

    Examples:
        - Negative amount
        - Zero amount
        - Amount exceeds maximum
    """

    def __init__(self, amount: int, reason: str):
        message = f"Invalid amount {amount}: {reason}"
        super().__init__(message, code="INVALID_AMOUNT")
        self.amount = amount
        self.reason = reason


class ValidationException(DomainException):
    """
    Raised when input validation fails.
    """

    def __init__(self, field: str, value: Any, reason: str):
        message = f"Validation failed for field '{field}': {reason}"
        super().__init__(message, code="VALIDATION_ERROR")
        self.field = field
        self.value = value
        self.reason = reason

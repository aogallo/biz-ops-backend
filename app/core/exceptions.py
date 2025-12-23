"""Custom exception classes for the application."""

from typing import Any


class AppException(Exception):
    """Base exception class for application errors."""

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        """Initialize the exception.

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            details: Additional error details
        """
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(AppException):
    """Raised when data validation fails."""

    def __init__(self, message: str, field: str | None = None, **kwargs):
        """Initialize validation error.

        Args:
            message: Error message
            field: Field that failed validation
            **kwargs: Additional details
        """
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details={"field": field, **kwargs},
        )


class NotFoundError(AppException):
    """Raised when a requested resource is not found."""

    def __init__(self, resource: str, identifier: Any):
        """Initialize not found error.

        Args:
            resource: Type of resource (e.g., "User", "Vendor")
            identifier: Identifier that was not found
        """
        super().__init__(
            message=f"{resource} with identifier '{identifier}' not found",
            error_code="NOT_FOUND",
            details={"resource": resource, "identifier": identifier},
        )


class AuthenticationError(AppException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        """Initialize authentication error.

        Args:
            message: Error message
        """
        super().__init__(message=message, error_code="AUTHENTICATION_ERROR")


class AuthorizationError(AppException):
    """Raised when authorization fails."""

    def __init__(
        self,
        message: str = "Insufficient permissions",
        resource: str | None = None,
    ):
        """Initialize authorization error.

        Args:
            message: Error message
            resource: Resource that was denied
        """
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            details={"resource": resource} if resource else {},
        )


class DatabaseError(AppException):
    """Raised when a database operation fails."""

    def __init__(self, message: str, operation: str | None = None):
        """Initialize database error.

        Args:
            message: Error message
            operation: Database operation that failed
        """
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details={"operation": operation} if operation else {},
        )


class DuplicateError(AppException):
    """Raised when attempting to create a duplicate resource."""

    def __init__(self, resource: str, field: str, value: Any):
        """Initialize duplicate error.

        Args:
            resource: Type of resource
            field: Field that has duplicate value
            value: The duplicate value
        """
        super().__init__(
            message=f"{resource} with {field}='{value}' already exists",
            error_code="DUPLICATE_ERROR",
            details={"resource": resource, "field": field, "value": value},
        )

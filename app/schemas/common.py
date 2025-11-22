"""Common schemas used across the API."""

from typing import Any

from pydantic import Field

from app.schemas.base import CamelCaseSchema


class ErrorResponse(CamelCaseSchema):
    """Standard error response schema."""

    detail: str = Field(..., description="Error message")
    error_code: str | None = Field(
        None, description="Error code for client handling"
    )
    field: str | None = Field(None, description="Field that caused the error")


class HealthResponse(CamelCaseSchema):
    """Health check response schema."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    database: str = Field(..., description="Database connection status")


class MessageResponse(CamelCaseSchema):
    """Generic message response."""

    message: str
    data: Any | None = None

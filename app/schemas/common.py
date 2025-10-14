"""Common schemas used across the API."""
from typing import Any, Optional

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code for client handling")
    field: Optional[str] = Field(None, description="Field that caused the error")


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    database: str = Field(..., description="Database connection status")


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str
    data: Optional[Any] = None




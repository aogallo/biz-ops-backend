"""Common schemas used across the API."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    detail: str = Field(..., description="Error message")
    error_code: str | None = Field(
        None,
        description="Error code for client handling",
        serialization_alias="errorCode",
    )
    field: str | None = Field(None, description="Field that caused the error")


class HealthResponse(BaseModel):
    """Health check response schema."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    database: str = Field(..., description="Database connection status")


class MessageResponse(BaseModel):
    """Generic message response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    message: str
    data: Any | None = None

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AccountCreate(BaseModel):
    """Schema for creating a new account."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    name: str
    account_number: str = Field(serialization_alias="accountNumber")
    type: str


class AccountResponse(BaseModel):
    """Schema for account response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    name: str
    account_number: str = Field(serialization_alias="accountNumber")
    type: str
    created_by: str = Field(serialization_alias="createdBy")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_by: str | None = Field(serialization_alias="updatedBy")
    updated_at: datetime | None = Field(serialization_alias="updatedAt")

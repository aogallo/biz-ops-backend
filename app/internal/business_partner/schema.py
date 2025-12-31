"""BusinessPartner API schemas for requests and responses."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.common import PaginationResponse


class BusinessPartnerCreate(BaseModel):
    """Schema for creating a new customer."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    name: str
    nit: str
    date_birth: str | None = Field(
        default=None, serialization_alias="dateBirth"
    )
    commercial_activity: str | None = Field(
        default=None, serialization_alias="commercialActivity"
    )
    email: EmailStr
    address: str | None = None


class BusinessPartnerUpdate(BaseModel):
    """Schema for updating a customer."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    name: str | None = None
    nit: str | None = None
    date_birth: str | None = Field(
        default=None, serialization_alias="dateBirth"
    )
    commercial_activity: str | None = Field(
        default=None, serialization_alias="commercialActivity"
    )
    email: EmailStr | None = None
    address: str | None = None


class BusinessPartnerResponse(BaseModel):
    """Schema for customer response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    name: str
    nit: str
    date_birth: str | None = Field(serialization_alias="dateBirth")
    commercial_activity: str | None = Field(
        serialization_alias="commercialActivity"
    )
    email: EmailStr
    address: str | None
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime | None = Field(serialization_alias="updatedAt")


class BusinessPartnerListResponse(BaseModel):
    """Schema for list of customers response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    customers: list[BusinessPartnerResponse]
    pagination: PaginationResponse

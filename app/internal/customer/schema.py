"""Customer API schemas for requests and responses."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CustomerCreate(BaseModel):
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


class CustomerUpdate(BaseModel):
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


class CustomerResponse(BaseModel):
    """Schema for customer response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
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


class CustomerListResponse(BaseModel):
    """Schema for list of customers response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    customers: list[CustomerResponse]
    total: int = Field(description="Total number of customers")

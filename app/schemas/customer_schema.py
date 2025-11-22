"""Customer API schemas for requests and responses."""

from datetime import datetime

from pydantic import EmailStr, Field

from app.schemas.base import CamelCaseSchema


class CustomerCreate(CamelCaseSchema):
    """Schema for creating a new customer."""

    name: str
    nit: str
    date_birth: str | None = None
    commercial_activity: str | None = None
    email: EmailStr
    address: str | None = None


class CustomerUpdate(CamelCaseSchema):
    """Schema for updating a customer."""

    name: str | None = None
    nit: str | None = None
    date_birth: str | None = None
    commercial_activity: str | None = None
    email: EmailStr | None = None
    address: str | None = None


class CustomerResponse(CamelCaseSchema):
    """Schema for customer response."""

    id: int
    name: str
    nit: str
    date_birth: str | None
    commercial_activity: str | None
    email: EmailStr
    address: str | None
    created_by: str
    created_at: datetime
    updated_by: str | None
    updated_at: datetime | None


class CustomerListResponse(CamelCaseSchema):
    """Schema for list of customers response."""

    customers: list[CustomerResponse]
    total: int = Field(description="Total number of customers")

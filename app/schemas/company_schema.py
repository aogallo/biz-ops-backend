"""Company API schemas for requests and responses."""

from datetime import datetime

from pydantic import EmailStr

from app.schemas.base import CamelCaseSchema


class CompanyCreate(CamelCaseSchema):
    """Schema for creating a new company."""

    name: str
    nit: str
    date_birth: str | None = None
    commercial_activity: str | None = None
    email: EmailStr
    address: str | None = None


class CompanyUpdate(CamelCaseSchema):
    """Schema for updating a company."""

    name: str | None = None
    nit: str | None = None
    date_birth: str | None = None
    commercial_activity: str | None = None
    email: EmailStr | None = None
    address: str | None = None


class CompanyResponse(CamelCaseSchema):
    """Schema for company response."""

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


class CompaniesResponse(CamelCaseSchema):
    """Schema for list of companies response."""

    count: int
    data: list[CompanyResponse]

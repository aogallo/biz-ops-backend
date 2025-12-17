"""Company API schemas for requests and responses."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.common import PaginationResponse


class CompanyCreate(BaseModel):
    """Schema for creating a new company."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    name: str
    nit: str
    date_birth: str | None = Field(
        default=None, alias="dateBirth", serialization_alias="dateBirth"
    )
    commercial_activity: str | None = Field(
        default=None,
        alias="commercialActivity",
        serialization_alias="commercialActivity",
    )
    email: EmailStr
    address: str | None = None
    managed_by_accountant: bool = Field(
        default=False,
        alias="managedByAccountant",
        serialization_alias="managedByAccountant",
    )


class CompanyUpdate(BaseModel):
    """Schema for updating a company."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    name: str | None = None
    nit: str | None = None
    date_birth: str | None = Field(
        default=None, alias="dateBirth", serialization_alias="dateBirth"
    )
    commercial_activity: str | None = Field(
        default=None,
        alias="commercialActivity",
        serialization_alias="commercialActivity",
    )
    email: EmailStr | None = None
    address: str | None = None
    managed_by_accountant: bool | None = Field(
        default=None,
        alias="managedByAccountant",
        serialization_alias="managedByAccountant",
    )


class CompanyResponse(BaseModel):
    """Schema for company response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    nit: str
    date_birth: str | None = Field(serialization_alias="dateBirth")
    commercial_activity: str | None = Field(
        serialization_alias="commercialActivity"
    )
    email: str | None
    address: str | None
    managed_by_accountant: bool = Field(
        serialization_alias="managedByAccountant"
    )
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime | None = Field(serialization_alias="updatedAt")


class CompanyListResponse(BaseModel):
    """Schema for list of companies response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    companies: list[CompanyResponse]
    pagination: PaginationResponse


class CompanyMinimalResponse(BaseModel):
    """Schema for company response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    email: str | None
    nit: str

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.internal.organization.entity import Organization
from app.schemas.common import PaginationResponse


class OrganizationCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    name: str
    slug: str
    contact_name: str | None = Field(
        default=None, serialization_alias="contactName"
    )
    contact_email: str | None = Field(
        default=None, serialization_alias="contactEmail"
    )
    contact_phone: str | None = Field(
        default=None, serialization_alias="contactPhone"
    )
    address_line_1: str | None = Field(
        default=None, serialization_alias="addressLine1"
    )
    address_line_2: str | None = Field(
        default=None, serialization_alias="addressLine2"
    )
    city: str | None = None
    state: str | None = None
    country: str | None = None
    postal_code: str | None = Field(
        serialization_alias="postalCode", default=None
    )
    settings: dict = {}
    is_active: bool = Field(default=True, serialization_alias="isActive")


class OrganizationResponse(OrganizationCreate):
    id: UUID


class OrganizationListResponse(BaseModel):
    organizations: list[OrganizationResponse]
    pagination: PaginationResponse


class OrganizationList(BaseModel):
    """Service layer response for paginated company list.

    This is the contract between CompanyService and route handlers.
    Route handlers convert this to CompanyListResponse (API schema).
    """

    model_config = ConfigDict(frozen=True, from_attributes=True)

    count: int = Field(..., description="Total number of organization")
    organizations: list[Organization] = Field(
        ..., description="List of organizations entities"
    )

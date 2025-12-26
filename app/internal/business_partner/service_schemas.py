"""Service layer response schemas for customer operations.

These schemas define the contract between service and route layers.
They are distinct from API schemas to separate internal and external contracts.
"""

from app.internal.business_partner.entity import BusinessPartner
from pydantic import BaseModel, ConfigDict, Field


class BusinessPartnerListServiceResponse(BaseModel):
    """Service layer response for paginated customer list.

    This is the contract between BusinessPartnerService and route handlers.
    Route handlers convert this to BusinessPartnerListResponse (API schema).
    """

    model_config = ConfigDict(frozen=True, from_attributes=True)

    count: int = Field(..., description="Total number of customers")
    customers: list[BusinessPartner] = Field(
        ..., description="List of customer entities"
    )

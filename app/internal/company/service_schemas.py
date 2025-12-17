"""Service layer response schemas for company operations.

These schemas define the contract between service and route layers.
They are distinct from API schemas to separate internal and external contracts.
"""

from pydantic import BaseModel, ConfigDict, Field

from app.internal.company.entity import Company


class CompanyListServiceResponse(BaseModel):
    """Service layer response for paginated company list.

    This is the contract between CompanyService and route handlers.
    Route handlers convert this to CompanyListResponse (API schema).
    """

    model_config = ConfigDict(frozen=True, from_attributes=True)

    count: int = Field(..., description="Total number of companies")
    companies: list[Company] = Field(
        ..., description="List of company entities"
    )

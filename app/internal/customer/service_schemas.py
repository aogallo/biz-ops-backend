"""Service layer response schemas for customer operations.

These schemas define the contract between service and route layers.
They are distinct from API schemas to separate internal and external contracts.
"""

from pydantic import BaseModel, ConfigDict, Field

from app.internal.customer.entity import Customer


class CustomerListServiceResponse(BaseModel):
    """Service layer response for paginated customer list.

    This is the contract between CustomerService and route handlers.
    Route handlers convert this to CustomerListResponse (API schema).
    """

    model_config = ConfigDict(frozen=True, from_attributes=True)

    count: int = Field(..., description="Total number of customers")
    customers: list[Customer] = Field(
        ..., description="List of customer entities"
    )

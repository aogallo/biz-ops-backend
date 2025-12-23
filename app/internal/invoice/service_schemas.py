"""Service layer response schemas for invoice operations.

These schemas define the contract between service and route layers.
They are distinct from API schemas to separate internal and external contracts.
"""

from pydantic import BaseModel, ConfigDict, Field

from app.internal.invoice.entity import Invoice


class InvoiceListServiceResponse(BaseModel):
    """Service layer response for paginated invoice list.

    This is the contract between InvoiceService and route handlers.
    Route handlers convert this to InvoiceListResponse (API schema).
    """

    model_config = ConfigDict(frozen=True, from_attributes=True)

    count: int = Field(..., description="Total number of invoices")
    invoices: list[Invoice] = Field(
        ..., description="List of invoice entities"
    )

"""Invoice API schemas for requests and responses."""

from datetime import datetime
from typing import Literal

from pydantic import Field

from app.schemas.base import CamelCaseSchema
from app.schemas.invoice_detail_schema import InvoiceDetailResponse

InvoiceState = Literal["draft", "open", "paid", "void"]


class InvoiceCreate(CamelCaseSchema):
    """Schema for creating a new invoice."""

    date: datetime
    authorization_number: str
    dte_type: str
    serie: str
    dte_number: str
    company_id: int
    customer_id: int
    currency: str = "GTQ"
    state: InvoiceState = "draft"


class InvoiceUpdate(CamelCaseSchema):
    """Schema for updating an invoice."""

    date: datetime | None = None
    authorization_number: str | None = None
    dte_type: str | None = None
    serie: str | None = None
    dte_number: str | None = None
    company_id: int | None = None
    customer_id: int | None = None
    currency: str | None = None
    state: str | None = None
    is_cancelled: bool | None = None
    cancelled_date: datetime | None = None


class InvoiceResponse(CamelCaseSchema):
    """Schema for invoice response."""

    id: int
    date: datetime
    authorization_number: str
    dte_type: str
    serie: str
    dte_number: str
    company_id: int
    customer_id: int
    currency: str
    subtotal: float
    total_taxes: float
    total_amount: float
    state: InvoiceState
    is_cancelled: bool | None
    cancelled_date: datetime | None
    created_by: str
    created_at: datetime
    updated_by: str | None
    updated_at: datetime | None

    # Optional nested details
    details: list[InvoiceDetailResponse] | None = None


class InvoiceListResponse(CamelCaseSchema):
    """Schema for list of invoices response."""

    invoices: list[InvoiceResponse]
    total: int = Field(description="Total number of invoices")

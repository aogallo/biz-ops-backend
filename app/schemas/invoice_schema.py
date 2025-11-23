"""Invoice API schemas for requests and responses."""
import math
from datetime import datetime
from typing import Literal

from pydantic import Field, field_validator
from sqlmodel import SQLModel

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


class InvoiceRowSchema(SQLModel):
    date: str
    authorization_number: str
    dte_type: str
    serie: str
    dte_number: int
    exportation: bool
    company_nit: str
    company_name: str
    company_description: str
    company_code: int
    customer_nit: str
    customer_name: str
    certificator_nit: int
    certificator_name: str
    state: str
    money: str
    total: float
    iva: float
    is_voided: bool
    voided_date: str
    petroleum: float
    hotel: float
    tickets: float
    # Timbre de Prensa
    press_stamp: float
    firefigthers: float
    municipal_tax: float
    alcoholic_tax: float
    tobacco_tax: float
    cement_tax: float
    no_alcoholic_tax: float
    port_tariff_tax: float

    @field_validator("is_voided", mode="before")
    @classmethod
    def transform_is_voided(cls, v: str) -> bool:
        if v == "No":
            return False
        else:
            return True

    @field_validator("voided_date", mode="before")
    @classmethod
    def transform_voided_date(cls, v: str) -> str | None:
        if isinstance(v, float) and math.isnan(v):
            return ""
        return v

    @field_validator("customer_nit", mode="before")
    @classmethod
    def transform_customer_nit(cls, value: str):
        return str(value)

    @field_validator("company_nit", mode="before")
    @classmethod
    def transform_company_nit(cls, value: str):
        return str(value)

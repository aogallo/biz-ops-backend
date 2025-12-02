"""Invoice API schemas for requests and responses."""

import math
from datetime import datetime
from typing import Literal

from pydantic import Field, field_validator
from sqlmodel import SQLModel

from app.internal.invoices.invoice_detail_schema import InvoiceDetailResponse
from app.schemas.base import CamelCaseSchema
from app.schemas.company_schema import CompanyResponse
from app.schemas.customer_schema import CustomerResponse

InvoiceState = Literal["draft", "open", "paid", "void", "Vigente"]


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
    account_id: int | None = None


class InvoiceResponse(CamelCaseSchema):
    """Schema for invoice response."""

    id: int
    date: datetime
    authorization_number: str
    dte_type: str
    serie: str
    dte_number: str
    currency: str
    subtotal: float
    total_taxes: float
    total_amount: float
    state: InvoiceState
    is_cancelled: bool | None
    cancelled_date: datetime | None
    created_at: datetime
    updated_at: datetime | None
    invoice_type: str

    # Optional nested details
    details: list[InvoiceDetailResponse] | None = None

    company: CompanyResponse | None = None

    customer: CustomerResponse | None = None


class InvoiceListResponse(CamelCaseSchema):
    """Schema for list of invoices response."""

    invoices: list[InvoiceResponse]
    total: int = Field(description="Total number of invoices")


class InvoiceRowSchema(SQLModel):
    """Schema for invoice row."""

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
        """Transform is_voided to boolean."""
        if v == "No":
            return False
        else:
            return True

    @field_validator("voided_date", mode="before")
    @classmethod
    def transform_voided_date(cls, v: str) -> str | None:
        """Transform voided_date to string."""
        if isinstance(v, float) and math.isnan(v):
            return ""
        return v

    @field_validator("customer_nit", mode="before")
    @classmethod
    def transform_customer_nit(cls, value: str):
        """Transform customer_nit to string."""
        return str(value)

    @field_validator("company_nit", mode="before")
    @classmethod
    def transform_company_nit(cls, value: str):
        """Transform company_nit to string."""
        return str(value)


class UniqueCustomers(CamelCaseSchema):
    """Schema for unique customers."""

    name: str
    nit: str

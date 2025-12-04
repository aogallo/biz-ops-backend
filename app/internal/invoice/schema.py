"""Invoice API schemas for requests and responses."""

import math
from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import Field, field_validator
from sqlmodel import SQLModel

from app.internal.account.entity import Account
from app.internal.company.schema import CompanyResponse
from app.internal.customer.schema import CustomerResponse
from app.schemas.base import CamelCaseSchema

InvoiceState = Literal["draft", "open", "paid", "void", "Vigente"]


class InvoiceDetailResponse(CamelCaseSchema):
    """Schema for invoice detail response."""

    id: int
    invoice_id: int
    product_code: str | None
    product_name: str
    description: str | None
    quantity: float
    unit_price: float

    # Tax details
    iva: float | None
    petroleo: float | None
    turismo_hospedaje: float | None
    turismo_pasajes: float | None
    timbre_prensa: float | None
    bomberos: float | None
    tasa_municipal: float | None
    bebidas_alcoholicas: float | None
    tabaco: float | None
    cemento: float | None
    bebidas_no_alcoholicas: float | None
    tarifa_portuaria: float | None

    # Calculated fields
    subtotal: float
    total_taxes: float
    total: float

    created_by: str
    created_at: datetime
    updated_by: str | None
    updated_at: datetime | None


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

    account: Account | None = None


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
    dte_number: str
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

    @field_validator("dte_number", mode="before")
    @classmethod
    def transform_dte_number(cls, value: str):
        """Transform dte_number to string."""
        return str(value)


class UniqueCustomers(CamelCaseSchema):
    """Schema for unique customers."""

    name: str
    nit: str


class InvoiceDetailCreate(CamelCaseSchema):
    """Schema for creating a new invoice detail."""

    invoice_id: int
    product_code: str | None = None
    product_name: str
    description: str | None = None
    quantity: float
    unit_price: float

    # Tax details
    iva: float | None = 0.0
    petroleo: float | None = 0.0
    turismo_hospedaje: float | None = 0.0
    turismo_pasajes: float | None = 0.0
    timbre_prensa: float | None = 0.0
    bomberos: float | None = 0.0
    tasa_municipal: float | None = 0.0
    bebidas_alcoholicas: float | None = 0.0
    tabaco: float | None = 0.0
    cemento: float | None = 0.0
    bebidas_no_alcoholicas: float | None = 0.0
    tarifa_portuaria: float | None = 0.0


class InvoiceDetailUpdate(CamelCaseSchema):
    """Schema for updating an invoice detail."""

    product_code: str | None = None
    product_name: str | None = None
    description: str | None = None
    quantity: float | None = None
    unit_price: float | None = None
    iva: float | None = None
    petroleo: float | None = None
    turismo_hospedaje: float | None = None
    turismo_pasajes: float | None = None
    timbre_prensa: float | None = None
    bomberos: float | None = None
    tasa_municipal: float | None = None
    bebidas_alcoholicas: float | None = None
    tabaco: float | None = None
    cemento: float | None = None
    bebidas_no_alcoholicas: float | None = None
    tarifa_portuaria: float | None = None


class InvoiceUpdateAccount(CamelCaseSchema):
    """Schema for updating an invoice account."""

    account_id: int


class InvoiceType(str, Enum):
    EXPENSES = "EXPENSES"
    INCOMES = "INCOMES"

"""Invoice API schemas for requests and responses."""

import math
from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlmodel import SQLModel

from app.internal.account.entity import Account
from app.internal.company.schema import CompanyResponse
from app.internal.customer.schema import CustomerResponse
from app.schemas.common import PaginationResponse

InvoiceState = Literal["draft", "open", "paid", "void", "Vigente"]


class InvoiceDetailResponse(BaseModel):
    """Schema for invoice detail response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    invoice_id: int = Field(serialization_alias="invoiceId")
    product_code: str | None = Field(serialization_alias="productCode")
    product_name: str = Field(serialization_alias="productName")
    description: str | None
    quantity: float
    unit_price: float = Field(serialization_alias="unitPrice")

    # Tax details
    iva: float | None
    petroleo: float | None
    turismo_hospedaje: float | None = Field(
        serialization_alias="turismoHospedaje"
    )
    turismo_pasajes: float | None = Field(serialization_alias="turismoPasajes")
    timbre_prensa: float | None = Field(serialization_alias="timbrePrensa")
    bomberos: float | None
    tasa_municipal: float | None = Field(serialization_alias="tasaMunicipal")
    bebidas_alcoholicas: float | None = Field(
        serialization_alias="bebidasAlcoholicas"
    )
    tabaco: float | None
    cemento: float | None
    bebidas_no_alcoholicas: float | None = Field(
        serialization_alias="bebidasNoAlcoholicas"
    )
    tarifa_portuaria: float | None = Field(
        serialization_alias="tarifaPortuaria"
    )

    # Calculated fields
    subtotal: float
    total_taxes: float = Field(serialization_alias="totalTaxes")
    total: float

    created_by: str = Field(serialization_alias="createdBy")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_by: str | None = Field(serialization_alias="updatedBy")
    updated_at: datetime | None = Field(serialization_alias="updatedAt")


class InvoiceCreate(BaseModel):
    """Schema for creating a new invoice."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    date: datetime
    authorization_number: str = Field(
        serialization_alias="authorizationNumber"
    )
    dte_type: str = Field(serialization_alias="dteType")
    serie: str
    dte_number: str = Field(serialization_alias="dteNumber")
    company_id: int = Field(serialization_alias="companyId")
    customer_id: int = Field(serialization_alias="customerId")
    currency: str = "GTQ"
    state: InvoiceState = "draft"


class InvoiceUpdate(BaseModel):
    """Schema for updating an invoice."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    date: datetime | None = None
    authorization_number: str | None = Field(
        default=None, serialization_alias="authorizationNumber"
    )
    dte_type: str | None = Field(default=None, serialization_alias="dteType")
    serie: str | None = None
    dte_number: str | None = Field(
        default=None, serialization_alias="dteNumber"
    )
    company_id: int | None = Field(
        default=None, serialization_alias="companyId"
    )
    customer_id: int | None = Field(
        default=None, serialization_alias="customerId"
    )
    currency: str | None = None
    state: str | None = None
    is_cancelled: bool | None = Field(
        default=None, serialization_alias="isCancelled"
    )
    cancelled_date: datetime | None = Field(
        default=None, serialization_alias="cancelledDate"
    )
    account_id: int | None = Field(
        default=None, serialization_alias="accountId"
    )


class InvoiceResponse(BaseModel):
    """Schema for invoice response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    date: datetime
    authorization_number: str = Field(
        serialization_alias="authorizationNumber"
    )
    dte_type: str = Field(serialization_alias="dteType")
    serie: str
    dte_number: str = Field(serialization_alias="dteNumber")
    currency: str
    subtotal: float
    total_taxes: float = Field(serialization_alias="totalTaxes")
    total_amount: float = Field(serialization_alias="totalAmount")
    state: InvoiceState
    is_cancelled: bool | None = Field(serialization_alias="isCancelled")
    cancelled_date: datetime | None = Field(
        serialization_alias="cancelledDate"
    )
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime | None = Field(serialization_alias="updatedAt")
    invoice_type: str = Field(serialization_alias="invoiceType")

    # Optional nested details
    details: list[InvoiceDetailResponse] | None = None

    company: CompanyResponse | None = None

    customer: CustomerResponse | None = None

    account: Account | None = None


class InvoiceListResponse(BaseModel):
    """Schema for list of invoices response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

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


class UniqueCustomers(BaseModel):
    """Schema for unique customers."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    name: str
    nit: str


class InvoiceDetailCreate(BaseModel):
    """Schema for creating a new invoice detail."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    invoice_id: int = Field(serialization_alias="invoiceId")
    product_code: str | None = Field(
        default=None, serialization_alias="productCode"
    )
    product_name: str = Field(serialization_alias="productName")
    description: str | None = None
    quantity: float
    unit_price: float = Field(serialization_alias="unitPrice")

    # Tax details
    iva: float | None = 0.0
    petroleo: float | None = 0.0
    turismo_hospedaje: float | None = Field(
        default=0.0, serialization_alias="turismoHospedaje"
    )
    turismo_pasajes: float | None = Field(
        default=0.0, serialization_alias="turismoPasajes"
    )
    timbre_prensa: float | None = Field(
        default=0.0, serialization_alias="timbrePrensa"
    )
    bomberos: float | None = 0.0
    tasa_municipal: float | None = Field(
        default=0.0, serialization_alias="tasaMunicipal"
    )
    bebidas_alcoholicas: float | None = Field(
        default=0.0, serialization_alias="bebidasAlcoholicas"
    )
    tabaco: float | None = 0.0
    cemento: float | None = 0.0
    bebidas_no_alcoholicas: float | None = Field(
        default=0.0, serialization_alias="bebidasNoAlcoholicas"
    )
    tarifa_portuaria: float | None = Field(
        default=0.0, serialization_alias="tarifaPortuaria"
    )


class InvoiceDetailUpdate(BaseModel):
    """Schema for updating an invoice detail."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    product_code: str | None = Field(
        default=None, serialization_alias="productCode"
    )
    product_name: str | None = Field(
        default=None, serialization_alias="productName"
    )
    description: str | None = None
    quantity: float | None = None
    unit_price: float | None = Field(
        default=None, serialization_alias="unitPrice"
    )
    iva: float | None = None
    petroleo: float | None = None
    turismo_hospedaje: float | None = Field(
        default=None, serialization_alias="turismoHospedaje"
    )
    turismo_pasajes: float | None = Field(
        default=None, serialization_alias="turismoPasajes"
    )
    timbre_prensa: float | None = Field(
        default=None, serialization_alias="timbrePrensa"
    )
    bomberos: float | None = None
    tasa_municipal: float | None = Field(
        default=None, serialization_alias="tasaMunicipal"
    )
    bebidas_alcoholicas: float | None = Field(
        default=None, serialization_alias="bebidasAlcoholicas"
    )
    tabaco: float | None = None
    cemento: float | None = None
    bebidas_no_alcoholicas: float | None = Field(
        default=None, serialization_alias="bebidasNoAlcoholicas"
    )
    tarifa_portuaria: float | None = Field(
        default=None, serialization_alias="tarifaPortuaria"
    )


class InvoiceUpdateAccount(BaseModel):
    """Schema for updating an invoice account."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    account_id: int = Field(serialization_alias="accountId")


class InvoiceType(str, Enum):
    EXPENSES = "expenses"
    INCOMES = "incomes"


class InvoicePaginationResponse(BaseModel):
    """Schema for pagination response."""

    data: list[InvoiceResponse]
    pagination: PaginationResponse

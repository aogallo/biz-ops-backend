"""Invoice Detail API schemas for requests and responses."""

from datetime import datetime

from app.schemas.base import CamelCaseSchema


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

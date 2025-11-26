from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.domain.entities.invoice import Invoice


class InvoiceDetailBase(SQLModel):
    """
    Base invoice detail
    """

    # Product/Service information
    product_code: str | None = None
    product_name: str
    description: str | None = None
    quantity: float
    unit_price: float

    # Tax details
    iva: float | None = 0.0  # VAT amount
    petroleo: float | None = 0.0  # Petroleum tax
    turismo_hospedaje: float | None = 0.0  # Tourism lodging tax
    turismo_pasajes: float | None = 0.0  # Tourism transport tax
    timbre_prensa: float | None = 0.0  # Newspaper stamp tax
    bomberos: float | None = 0.0  # Firefighters tax
    tasa_municipal: float | None = 0.0  # Municipal rate
    bebidas_alcoholicas: float | None = 0.0  # Alcoholic beverages tax
    tabaco: float | None = 0.0  # Tobacco tax
    cemento: float | None = 0.0  # Cement tax
    bebidas_no_alcoholicas: float | None = 0.0  # Non-alcoholic beverages tax
    tarifa_portuaria: float | None = 0.0  # Port tariff

    # Calculated fields
    subtotal: float = Field(default=0.0)  # quantity * unit_price
    total_taxes: float = Field(default=0.0)  # sum of all taxes
    total: float = Field(default=0.0)  # subtotal + total_taxes


class InvoiceDetailCreate(InvoiceDetailBase):
    """
    Create invoice detail
    """

    pass


class InvoiceDetailUpdate(SQLModel):
    """
    Update invoice detail
    """

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


class InvoiceDetail(InvoiceDetailBase, table=True):
    """
    Invoice detail entity
    """

    id: int | None = Field(default=None, primary_key=True)

    created_by: str = Field(index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_by: str | None = Field(default=None, index=True)
    updated_at: datetime | None = Field(default=None)

    # Relationships
    invoice_id: int | None = Field(default=None, foreign_key="invoice.id")
    invoice: "Invoice" = Relationship(back_populates="details")

    def calculate_totals(self):
        """Calculate subtotal, total taxes, and total"""
        self.subtotal = self.quantity * self.unit_price
        self.total_taxes = (
            (self.iva or 0)
            + (self.petroleo or 0)
            + (self.turismo_hospedaje or 0)
            + (self.turismo_pasajes or 0)
            + (self.timbre_prensa or 0)
            + (self.bomberos or 0)
            + (self.tasa_municipal or 0)
            + (self.bebidas_alcoholicas or 0)
            + (self.tabaco or 0)
            + (self.cemento or 0)
            + (self.bebidas_no_alcoholicas or 0)
            + (self.tarifa_portuaria or 0)
        )
        self.total = self.subtotal + self.total_taxes

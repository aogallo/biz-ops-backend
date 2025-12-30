from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, ClassVar, Literal
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from app.internal.shared.entity import TimestampMixin

if TYPE_CHECKING:
    from app.internal.account.entity import Account
    from app.internal.business_partner.entity import BusinessPartner
    from app.internal.company.entity import Company

InvoiceState = Literal["draft", "open", "paid", "void"]


class InvoiceOrigin(str, Enum):
    """Invoice origin classification."""

    LOCAL = "local"
    IMPORTED = "imported"


class InvoiceItemType(str, Enum):
    """Invoice item type classification."""

    GOODS = "goods"
    SERVICES = "services"


class InvoiceTaxStatus(str, Enum):
    """Invoice tax status classification."""

    TAXED = "taxed"
    EXEMPT = "exempt"


class InvoiceBase(SQLModel):
    """Base invoice model."""

    date: datetime
    authorization_number: str
    dte_type: str
    serie: str = Field(index=True)
    dte_number: str

    # income or expenses
    invoice_type: str = "expenses"

    currency: str = "GTQ"

    # Summary amounts (calculated from details)
    subtotal: float = Field(default=0.0)
    total_taxes: float = Field(default=0.0)
    total_amount: float = Field(default=0.0)

    # Classification dimensions (nullable - set by accountant after creation)
    origin: str | None = Field(default=None)  # InvoiceOrigin
    item_type: str | None = Field(default=None)  # InvoiceItemType
    tax_status: str | None = Field(default=None)  # InvoiceTaxStatus

    # State management
    state: str = "draft"
    is_cancelled: bool = False
    cancelled_date: datetime | None = None

    # SAT issuer and receiver names
    sat_issuer_name: str
    sat_receiver_name: str


class InvoiceCreate(InvoiceBase):
    """Create invoice schema."""

    business_partner_id: UUID


class InvoiceUpdate(SQLModel):
    """Update invoice schema."""

    date: datetime | None = None
    authorization_number: str | None = None
    dte_type: str | None = None
    serie: str | None = None
    dte_number: str | None = None
    currency: str | None = None
    state: str | None = None
    is_cancelled: bool | None = None
    cancelled_date: datetime | None = None


class InvoiceUpdateAccount(SQLModel):
    """Update account invoice schema."""

    account_id: UUID


class Invoice(InvoiceBase, TimestampMixin, table=True):
    """Invoice entity."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Foreign keys
    company_id: UUID = Field(foreign_key="company.id", index=True)
    business_partner_id: UUID = Field(
        foreign_key="business_partner.id", index=True
    )
    account_id: UUID | None = Field(
        foreign_key="account.id", index=True, default=None
    )

    created_by: str

    # Relationships
    company: "Company" = Relationship(back_populates="invoices")
    business_partner: "BusinessPartner" = Relationship()
    account: "Account" = Relationship()
    details: list["InvoiceDetail"] = Relationship(back_populates="invoice")

    def calculate_totals(self):
        """Calculate invoice totals from details"""
        if not self.details:
            self.subtotal = 0.0
            self.total_taxes = 0.0
            self.total_amount = 0.0
            return

        self.subtotal = sum(detail.subtotal for detail in self.details)
        self.total_taxes = sum(detail.total_taxes for detail in self.details)
        self.total_amount = self.subtotal + self.total_taxes


class InvoiceDetailBase(SQLModel):
    """Base invoice detail model."""

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
    """Create invoice detail schema."""

    pass


class InvoiceDetailUpdate(SQLModel):
    """Update invoice detail schema."""

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


class InvoiceDetail(InvoiceDetailBase, TimestampMixin, table=True):
    """Invoice detail entity."""

    __tablename__: ClassVar[str] = "invoice_detail"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Foreign key
    invoice_id: UUID | None = Field(default=None, foreign_key="invoice.id")

    # Relationship
    invoice: "Invoice" = Relationship(back_populates="details")

    created_by: str

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

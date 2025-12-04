from datetime import UTC, datetime
from typing import TYPE_CHECKING, Literal

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.internal.account.entity import Account
    from app.internal.company.entity import Company
    from app.internal.customer.entity import Customer

InvoiceState = Literal["draft", "open", "paid", "void"]


class InvoiceBase(SQLModel):
    """
    Base invoice
    """

    date: datetime
    authorization_number: str
    dte_type: str
    serie: str = Field(index=True)
    dte_number: str

    # income
    # expenses
    invoice_type: str = "expenses"

    company_id: int
    customer_id: int

    currency: str = "GTQ"

    # Summary amounts (calculated from details)
    subtotal: float = Field(default=0.0)
    total_taxes: float = Field(default=0.0)
    total_amount: float = Field(default=0.0)

    # Draft: The invoice is still being created and has not yet been sent
    # to the customer
    # Open / Due: The invoice has been finalized and sent,
    # but payment has not yet been received
    # Paid: The invoice has been paid in full
    # Void / Cancelled: The invoice was created by mistake and has been
    # cancelled

    state: str = "draft"
    is_cancelled: bool | None = False
    cancelled_date: datetime | None = None

    # journal_entries: list[JournalEntry] = Relationship(
    #     back_populates="journal_entry"
    # )
    #


class InvoiceCreate(InvoiceBase):
    """
    Create invoice
    """


class InvoiceUpdate(SQLModel):
    """
    Update invoice
    """

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


class InvoiceUpdateAccount(SQLModel):
    """
    Update account invoice
    """

    account_id: int


class Invoice(InvoiceBase, table=True):
    """
    Invoice entity
    """

    id: int | None = Field(default=None, primary_key=True)

    created_by: str = Field(index=True, default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_by: str | None = Field(default=None, index=True)
    updated_at: datetime | None = Field(default=None)

    # Relationship with company
    company_id: int = Field(foreign_key="company.id", index=True)
    company: "Company" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Invoice.company_id]"}
    )

    # Relationship with customer
    customer_id: int = Field(foreign_key="customer.id", index=True)
    customer: "Customer" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Invoice.customer_id]"}
    )

    # Relationship with account
    account_id: int | None = Field(
        foreign_key="account.id", index=True, default=None
    )
    account: "Account" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Invoice.account_id]"}
    )

    # Relationship with invoice details
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

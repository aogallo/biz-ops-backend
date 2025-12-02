from datetime import UTC, datetime
from typing import TYPE_CHECKING, Literal

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.domain.entities.company import Company
    from app.domain.entities.customer import Customer
    from app.internal.accounts.account_entity import Account
    from app.internal.invoices.invoice_detail_entity import InvoiceDetail

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
    invoiceType: str = "expenses"

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
    account_id: int | None = None


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

    # Relationship with accoutn
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

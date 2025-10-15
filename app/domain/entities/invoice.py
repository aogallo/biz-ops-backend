from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.domain.entities.customer import Customer
from app.domain.entities.journal_entry import JournalEntry

if TYPE_CHECKING:
    from app.domain.entities.invoice_detail import InvoiceDetail


class InvoiceBase(SQLModel):
    date: datetime
    authorization_number: str
    dte_type: str
    serie: str
    dte_number: str

    company_id: int = Field(foreign_key="customer.id")
    customer_id: int = Field(foreign_key="customer.id")

    currency: str = "GTQ"

    # Summary amounts (calculated from details)
    subtotal: float = Field(default=0.0)
    total_taxes: float = Field(default=0.0)
    total_amount: float = Field(default=0.0)

    state: str
    is_cancelled: bool | None = False
    cancelled_date: datetime | None = None

    # Relationships
    company: Customer = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Invoice.company_id]"}
    )
    customer: Customer = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Invoice.customer_id]"}
    )
    journal_entries: list[JournalEntry] = Relationship(
        back_populates="journal_entry"
    )


class InvoiceCreate(InvoiceBase):
    pass


class InvoiceUpdate(SQLModel):
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


class Invoice(InvoiceBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    created_by: str = Field(index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_by: str | None = Field(default=None, index=True)
    updated_at: datetime | None = Field(default=None)

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

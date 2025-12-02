from datetime import UTC, datetime

from sqlmodel import Field, Relationship, SQLModel

from app.internal.customer.customer_entity import Customer
from app.internal.invoice.invoice_entity import Invoice


class JournalEntryBase(SQLModel):
    """
    Base journal entry
    """

    company_id: int = Field(foreign_key="customer.id")
    invoice_id: int = Field(foreign_key="invoice.id")
    debit: float = Field(default=0)
    credit: float = Field(default=0)

    company: Customer = Relationship(back_populates="customer")
    invoice: Invoice = Relationship(back_populates="invoice")


class JournalEntryCreate(JournalEntryBase):
    """
    Create journal entry
    """

    pass


class JournalEntry(JournalEntryBase, table=True):
    """
    Journal entry entity
    """

    id: int | None = Field(default=None, primary_key=True)

    created_by: str = Field(index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_by: str | None = Field(default=None, index=True)
    updated_at: datetime | None = Field(default=None)

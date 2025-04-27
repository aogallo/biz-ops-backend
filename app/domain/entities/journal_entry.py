from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel

from app.domain.entities.customer import Customer
from app.domain.entities.invoice import Invoice


class JournalEntryBase(SQLModel):
    company_id: int = Field(foreign_key="customer.id")
    invoice_id: int = Field(foreign_key="invoice.id")
    debit: float = Field(default=0)
    credit: float = Field(default=0)

    company: Customer = Relationship(back_populates="customer")
    invoice: Invoice = Relationship(back_populates="invoice")


class JournalEntryCreate(JournalEntryBase):
    pass


class JournalEntry(JournalEntryBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    created_by: str = Field(index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: Optional[str] = Field(default=None, index=True)
    updated_at: Optional[datetime] = Field(default=None)

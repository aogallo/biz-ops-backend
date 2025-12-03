from datetime import UTC, datetime

from sqlmodel import Field, Relationship, SQLModel

from app.internal.account.entity import Account
from app.internal.company.entity import Company
from app.internal.invoice.entity import Invoice


class JournalEntryBase(SQLModel):
    """
    Base journal entry
    """

    company_id: int
    invoice_id: int
    account_id: int

    debit: float = Field(default=0)
    credit: float = Field(default=0)

    description: str


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

    account_id: int = Field(foreign_key="account.id")
    account: Account = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[JournalEntry.account_id]"}
    )

    company_id: int = Field(foreign_key="company.id")
    company: Company = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[JournalEntry.company_id]"}
    )

    invoice_id: int = Field(foreign_key="invoice.id")
    invoice: Invoice = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[JournalEntry.invoice_id]"}
    )

    created_by: str = Field(index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_by: str | None = Field(default=None, index=True)
    updated_at: datetime | None = Field(default=None)

from typing import TYPE_CHECKING, ClassVar, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from app.internal.shared.entity import TimestampMixin

if TYPE_CHECKING:
    from app.internal.account.entity import Account
    from app.internal.company.entity import Company
    from app.internal.invoice.entity import Invoice
    from app.internal.user.entity import User


class JournalEntryBase(SQLModel):
    """Base journal entry model."""

    debit: float = Field(default=0)
    credit: float = Field(default=0)
    description: str


class JournalEntryCreate(JournalEntryBase):
    """Create journal entry schema."""

    account_id: UUID
    invoice_id: UUID | None = None


class JournalEntry(JournalEntryBase, TimestampMixin, table=True):
    """
    Journal entry entity.
    Represents double-entry bookkeeping transactions.
    """

    __tablename__: ClassVar[str] = "journal_entry"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    created_by: str

    # Foreign keys
    company_id: UUID = Field(foreign_key="company.id", index=True)
    account_id: UUID = Field(foreign_key="account.id", index=True)
    invoice_id: UUID | None = Field(
        default=None, foreign_key="invoice.id", index=True
    )
    user_id: UUID | None = Field(
        default=None, foreign_key="user.id", index=True
    )

    # Relationships
    company: "Company" = Relationship(back_populates="journal_entries")
    account: "Account" = Relationship(back_populates="journal_entries")
    invoice: Optional["Invoice"] = Relationship(
        back_populates="journal_entries"
    )
    user: Optional["User"] = Relationship(back_populates="journal_entries")

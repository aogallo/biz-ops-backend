from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlmodel import JSON, Column, Field, Relationship, SQLModel

from app.internal.shared.entity import TimestampMixin

if TYPE_CHECKING:
    from app.internal.invoice.entity import Invoice
    from app.internal.journal.entity import JournalEntry
    from app.internal.organization.entity import Organization
    from app.internal.user.entity import UserCompanyAccess


class CompanyBase(SQLModel):
    name: str = Field(unique=True, index=True)
    nit: str = Field(unique=True, index=True)
    date_birth: str | None = Field(default=None)
    commercial_activity: str | None = Field(default=None)
    email: EmailStr | None = Field(
        default="no-email@example.com",
        nullable=True,
    )
    address: str | None = Field(default=None)
    managed_by_accountant: bool = Field(default=False)

    # Contact Info
    contact_name: str | None = Field(default=None, max_length=255)
    contact_email: str | None = Field(default=None, max_length=255)
    contact_phone: str | None = Field(default=None, max_length=50)

    # Address
    address_line_1: str | None = Field(default=None, max_length=255)
    address_line_2: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    postal_code: str | None = Field(default=None, max_length=20)

    # Settings
    settings: dict = Field(default={}, sa_column=Column(JSON))

    # Status
    is_active: bool = Field(default=True, index=True)

    # Accounting specific
    accounting_period_start: date | None = None
    accounting_period_end: date | None = None
    fiscal_year_end: str | None = Field(default=None, max_length=5)  # MM-DD
    currency: str = Field(default="GTQ", max_length=3)


class Company(CompanyBase, TimestampMixin, table=True):
    """
    Companies represent the clients of the accountant/organizations.
    All data is scoped to company id for multi-tenancy.
    """

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    organization_id: UUID = Field(
        foreign_key="organizations.id",
        nullable=False,
        index=True,
    )

    # Relationships
    organization: "Organization" = Relationship(back_populates="companies")
    invoices: list["Invoice"] = Relationship(back_populates="company")
    journal_entries: list["JournalEntry"] = Relationship(
        back_populates="company"
    )
    user_accesses: list["UserCompanyAccess"] = Relationship(
        back_populates="company"
    )


class CompanyCreate(CompanyBase):
    """Schema for creating a company."""

    organization_id: UUID

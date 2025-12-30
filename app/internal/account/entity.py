from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from app.internal.shared.entity import TimestampMixin

if TYPE_CHECKING:
    from app.internal.organization.entity import Organization


class AccountType(str, Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"


class AccountBase(SQLModel):
    """Base account model."""

    account_number: str = Field(index=True)
    name: str
    type: str


class AccountCreate(AccountBase):
    """Create account schema."""

    pass


class Account(AccountBase, TimestampMixin, table=True):
    """
    Account entity.
    Accounts are organization-scoped (shared across companies).
    """

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    organization_id: UUID = Field(
        foreign_key="organization.id",
        nullable=False,
        index=True,
    )

    # Relationships
    organization: "Organization" = Relationship(back_populates="accounts")

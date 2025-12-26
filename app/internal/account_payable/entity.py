from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from app.internal.shared.entity import TimestampMixin

if TYPE_CHECKING:
    from app.internal.business_partner.entity import BusinessPartner
    from app.internal.company.entity import Company


class AccountPayableBase(SQLModel):
    """Base account payable model."""

    amount: float
    description: str | None = None


class AccountPayableCreate(AccountPayableBase):
    """Create account payable schema."""

    business_partner_id: UUID


class AccountPayable(AccountPayableBase, TimestampMixin, table=True):
    """
    Account Payable entity (Cuentas por Pagar).
    Represents amounts owed to vendors/suppliers.
    """

    __tablename__ = "accounts_payable"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Foreign keys - FIXED: was pointing to customer.id, now points to companies.id
    company_id: UUID = Field(foreign_key="companies.id", index=True)
    business_partner_id: UUID = Field(
        foreign_key="business_partner.id", index=True
    )

    # Relationships
    company: "Company" = Relationship()
    business_partner: "BusinessPartner" = Relationship()

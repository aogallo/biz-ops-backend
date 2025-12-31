from typing import TYPE_CHECKING, ClassVar
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from app.internal.shared.entity import TimestampMixin

if TYPE_CHECKING:
    from app.internal.business_partner.entity import BusinessPartner
    from app.internal.company.entity import Company


class AccountReceivableBase(SQLModel):
    """Base account receivable model."""

    amount: float
    description: str | None = None


class AccountReceivableCreate(AccountReceivableBase):
    """Create account receivable schema."""

    business_partner_id: UUID


class AccountReceivable(AccountReceivableBase, TimestampMixin, table=True):
    """
    Account Receivable entity (Cuentas por Cobrar).
    Represents amounts owed by customers.
    """

    __tablename__: ClassVar[str] = "accounts_receivable"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Foreign keys
    company_id: UUID = Field(foreign_key="company.id", index=True)
    business_partner_id: UUID = Field(
        foreign_key="business_partner.id", index=True
    )

    # Relationships
    company: "Company" = Relationship(back_populates="accounts_receivable")
    business_partner: "BusinessPartner" = Relationship(
        back_populates="accounts_receivable"
    )

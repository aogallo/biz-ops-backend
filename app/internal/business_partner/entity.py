from typing import TYPE_CHECKING, ClassVar
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

from app.internal.shared.entity import TimestampMixin

if TYPE_CHECKING:
    # from app.internal.account_payable.entity import AccountPayable
    # from app.internal.account_receivable.entity import AccountReceivable
    from app.internal.invoice.entity import Invoice
    from app.internal.organization.entity import Organization


class BusinessPartnerBase(SQLModel):
    """Base business partner model."""

    name: str = Field(index=True)
    nit: str = Field(index=True)
    date_birth: str | None = Field(default=None)
    commercial_activity: str | None = Field(default=None)
    email: EmailStr | None = Field(
        default="no-email@example.com",
        nullable=True,
    )
    address: str | None = Field(default=None)
    is_vendor: bool
    is_customer: bool


class BusinessPartnerCreate(BusinessPartnerBase):
    """Create business partner schema."""

    pass


class BusinessPartner(BusinessPartnerBase, TimestampMixin, table=True):
    """
    Business Partner entity (Vendors and BusinessPartners).
    BusinessPartners are organization-scoped (shared across companies).
    Example: 'Los 3 pollos hermanos' vendor can be used across multiple client companies.
    """

    __tablename__: ClassVar[str] = "business_partner"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    organization_id: UUID = Field(
        foreign_key="organization.id",
        nullable=False,
        index=True,
    )
    created_by: str

    # Relationships
    organization: "Organization" = Relationship(
        back_populates="business_partners"
    )
    invoices: list["Invoice"] = Relationship(back_populates="business_partner")
    # accounts_payable: list["AccountPayable"] = Relationship(
    #     back_populates="business_partner"
    # )
    # accounts_receivable: list["AccountReceivable"] = Relationship(
    #     back_populates="business_partner"
    # )

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import JSON, Column, Field, Relationship, SQLModel

from app.internal.shared.entity import SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.internal.account.entity import Account
    from app.internal.business_partner.entity import BusinessPartner
    from app.internal.category.entity import Category
    from app.internal.company.entity import Company
    from app.internal.product.entity import Product
    from app.internal.user.entity import User


class OrganizationBase(SQLModel):
    """
    Represents accounting firms or accountants or direct clients.
    They will manage multiple companies (their clients).
    """

    name: str = Field(max_length=255, nullable=False)
    slug: str = Field(max_length=100, unique=True, nullable=False, index=True)

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


class Organization(OrganizationBase, TimestampMixin, SoftDeleteMixin, table=True):
    """Entity for Organization"""

    __tablename__ = "organizations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Optional: Subscription for billing (can be added later)
    subscription_id: UUID | None = Field(default=None, nullable=True)

    # Relationships
    companies: list["Company"] = Relationship(back_populates="organization")
    users: list["User"] = Relationship(back_populates="organization")
    business_partners: list["BusinessPartner"] = Relationship(
        back_populates="organization"
    )
    accounts: list["Account"] = Relationship(back_populates="organization")
    products: list["Product"] = Relationship(back_populates="organization")
    categories: list["Category"] = Relationship(back_populates="organization")

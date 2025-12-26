from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from app.internal.shared.entity import TimestampMixin

if TYPE_CHECKING:
    from app.internal.category.entity import Category
    from app.internal.organization.entity import Organization


class ProductBase(SQLModel):
    """Base product model."""

    name: str
    description: str | None = None
    price: float
    stock: int = 0


class ProductCreate(ProductBase):
    """Create product schema."""

    pass


class Product(ProductBase, TimestampMixin, table=True):
    """
    Product entity.
    Products are organization-scoped (shared across companies).
    """

    __tablename__ = "product"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    organization_id: UUID = Field(
        foreign_key="organizations.id",
        nullable=False,
        index=True,
    )
    category_id: UUID | None = Field(default=None, foreign_key="category.id")

    # Relationships
    organization: "Organization" = Relationship(back_populates="products")
    category: "Category" = Relationship()

from typing import TYPE_CHECKING, ClassVar
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from app.internal.shared.entity import TimestampMixin

if TYPE_CHECKING:
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

    __tablename__: ClassVar[str] = "product"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_by: str
    organization_id: UUID = Field(
        foreign_key="organization.id",
        nullable=False,
        index=True,
    )
    category_id: UUID | None = Field(default=None, foreign_key="category.id")

    # Relationships
    organization: "Organization" = Relationship(back_populates="products")

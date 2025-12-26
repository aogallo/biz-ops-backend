from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from app.internal.shared.entity import TimestampMixin

if TYPE_CHECKING:
    from app.internal.organization.entity import Organization


class CategoryBase(SQLModel):
    """Base category model."""

    name: str = Field(index=True)


class CategoryCreate(CategoryBase):
    """Create category schema."""

    pass


class Category(CategoryBase, TimestampMixin, table=True):
    """
    Category entity.
    Categories are organization-scoped (shared across companies).
    """

    __tablename__ = "category"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    organization_id: UUID = Field(
        foreign_key="organizations.id",
        nullable=False,
        index=True,
    )

    # Relationships
    organization: "Organization" = Relationship(back_populates="categories")

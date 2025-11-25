from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class CategoryBase(SQLModel):
    name: str = Field(unique=True)


class Category(CategoryBase, table=True):
    """
    Category entity
    """

    id: int | None = Field(default=None, primary_key=True)

    created_by: str = Field(index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_by: str | None = Field(default=None, index=True)
    updated_at: datetime | None = Field(default=None)


class CategoryCreate(CategoryBase):
    pass

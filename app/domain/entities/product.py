from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class ProductBase(SQLModel):
    """
    Base product
    """

    name: str
    description: str | None = None
    price: float
    stock: int = 0


class ProductCreate(ProductBase):
    pass


class Product(ProductBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    created_by: str = Field(index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_by: str | None = Field(default=None, index=True)
    updated_at: datetime | None = Field(default=None)

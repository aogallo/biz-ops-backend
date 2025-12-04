"""Product API schemas for requests and responses."""

from datetime import datetime

from pydantic import Field

from app.schemas.base import CamelCaseSchema


class ProductCreate(CamelCaseSchema):
    """Schema for creating a new product."""

    name: str
    description: str | None = None
    price: float
    stock: int = 0


class ProductUpdate(CamelCaseSchema):
    """Schema for updating a product."""

    name: str | None = None
    description: str | None = None
    price: float | None = None
    stock: int | None = None


class ProductResponse(CamelCaseSchema):
    """Schema for product response."""

    id: int
    name: str
    description: str | None
    price: float
    stock: int
    created_by: str
    created_at: datetime
    updated_by: str | None
    updated_at: datetime | None


class ProductListResponse(CamelCaseSchema):
    """Schema for list of products response."""

    products: list[ProductResponse]
    total: int = Field(description="Total number of products")

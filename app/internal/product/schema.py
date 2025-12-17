"""Product API schemas for requests and responses."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import PaginationResponse


class ProductCreate(BaseModel):
    """Schema for creating a new product."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    name: str
    description: str | None = None
    price: float
    stock: int = 0


class ProductUpdate(BaseModel):
    """Schema for updating a product."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    name: str | None = None
    description: str | None = None
    price: float | None = None
    stock: int | None = None


class ProductResponse(BaseModel):
    """Schema for product response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    description: str | None
    price: float
    stock: int
    created_by: str = Field(serialization_alias="createdBy")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_by: str | None = Field(serialization_alias="updatedBy")
    updated_at: datetime | None = Field(serialization_alias="updatedAt")


class ProductListResponse(BaseModel):
    """Schema for list of products response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    products: list[ProductResponse]
    pagination: PaginationResponse

"""Service layer response schemas for product operations.

These schemas define the contract between service and route layers.
They are distinct from API schemas to separate internal and external contracts.
"""

from pydantic import BaseModel, ConfigDict, Field

from app.internal.product.entity import Product


class ProductListServiceResponse(BaseModel):
    """Service layer response for paginated product list.

    This is the contract between ProductService and route handlers.
    Route handlers convert this to ProductListResponse (API schema).
    """

    model_config = ConfigDict(frozen=True, from_attributes=True)

    count: int = Field(..., description="Total number of products")
    products: list[Product] = Field(
        ..., description="List of product entities"
    )

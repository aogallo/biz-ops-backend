from fastapi import HTTPException, status

from app.domain.entities.product import Product, ProductCreate
from app.domain.entities.user import User
from app.infrastructure.repositories.product_repository_impl import (
    ProductRepositoryImpl,
)


class ProductService:
    """Service for managing products."""

    def __init__(self, current_user: User):
        self.repository = ProductRepositoryImpl(current_user)

    def create_product(self, product_request: ProductCreate) -> Product:
        """
        Create a new product.
        Raises error if product with same name exists.
        """
        # Check if product with same name already exists
        existing_product = self.repository.get_by_name(
            name=product_request.name
        )

        if existing_product is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The prodcut already exists",
            )

        # Create the new product
        return self.repository.create(product=product_request)

    def list_all_products(self) -> list[Product]:
        """Get all products."""
        return self.repository.get_all()

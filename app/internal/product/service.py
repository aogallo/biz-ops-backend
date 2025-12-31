from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import Session

from app.internal.product.entity import Product, ProductCreate
from app.internal.product.repository_impl import ProductRepositoryImpl
from app.internal.product.service_schemas import ProductListServiceResponse
from app.internal.user.entity import User


class ProductService:
    """Service for managing products (organization-scoped)."""

    def __init__(
        self,
        session: Session,
        current_user: User,
        organization_id: UUID,
    ):
        # Use provided organization_id or extract from current_user
        org_id = organization_id or current_user.organization_id
        if not org_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must belong to an organization",
            )
        self.repository = ProductRepositoryImpl(session, current_user, org_id)

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

    def list_all_products(
        self, offset: int, limit: int
    ) -> ProductListServiceResponse:
        """
        List all products with pagination.

        Args:
            offset: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            ProductListServiceResponse: Validated response with count and
                products
        """
        products = self.repository.get_all(offset=offset, limit=limit)
        count = self.repository.get_count()

        return ProductListServiceResponse(count=count, products=products)

from app.domain.entities.product import Product, ProductCreate
from app.infrastructure.database import get_current_session
from app.infrastructure.repositories.product_repository_impl import (
    ProductRepositoryImpl,
)


class ProductService:
    """Service for managing products."""

    def __init__(self):
        self.respository = ProductRepositoryImpl(session=get_current_session())

    def create_product(self, product_request: ProductCreate) -> Product | None:
        product_data = ProductCreate.model_dump_json(product_request)
        db_product = self.respository.get_by_name(name=product_data)

        if db_product is None:
            return None
        product_response = self.respository.create(product=product_request)
        return product_response

    def list_all_products(self) -> list[Product]:
        return self.respository.get_all()

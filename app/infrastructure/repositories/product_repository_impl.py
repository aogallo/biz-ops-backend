from typing import override

from sqlmodel import Session, select

from app.domain.entities.product import Product, ProductCreate
from app.domain.repositories.product_respository import ProductRepository
from app.infrastructure.database import get_current_session


class ProductRepositoryImpl(ProductRepository):
    """Implementation of Product Repository"""

    def __init__(self, session: Session | None = None) -> None:
        self.db = session or get_current_session()

    @override
    def create(self, product: ProductCreate) -> Product:
        """Create a new product"""
        db_product: Product = Product.model_validate(product)
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    @override
    def get_by_name(self, name: str) -> Product | None:
        """Get a product by name"""
        statement = select(Product).where(Product.name == name)
        product: Product | None = self.db.exec(
            statement=statement
        ).one_or_none()
        return product

    @override
    def get_by_id(self, product_id: int) -> Product | None:
        """Get a product by id"""
        product: Product | None = self.db.get(Product, product_id)
        return product

    @override
    def delete(self, product_id: int) -> bool:
        """Delete a product by id"""
        product: Product | None = self.db.get(Product, product_id)
        if product is None:
            return False
        self.db.delete(product)
        return True

    @override
    def get_all(self) -> list[Product]:
        """Get all products"""
        products: list[Product] = list(self.db.exec(select(Product)))
        return products

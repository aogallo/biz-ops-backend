from typing import override

from sqlmodel import Session, func, select

from app.internal.product.entity import Product, ProductCreate
from app.internal.product.respository import ProductRepository
from app.internal.user.entity import User


class ProductRepositoryImpl(ProductRepository):
    """Implementation of Product Repository"""

    def __init__(self, session: Session, current_user: User) -> None:
        self.db = session
        self.current_user = current_user

    @override
    def create(self, product: ProductCreate) -> Product:
        """Create a new product"""
        db_product: Product = Product.model_validate(
            product, update={"created_by": self.current_user.auth_id}
        )
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
    def get_all(self, offset: int, limit: int) -> list[Product]:
        """Get all products"""
        products: list[Product] = list(
            self.db.exec(select(Product).offset(offset).limit(limit))
        )
        return products

    def get_count(self) -> int:
        """Get count of products."""
        count_statement = select(func.count()).select_from(Product)
        count: int = self.db.exec(count_statement).one()
        return count

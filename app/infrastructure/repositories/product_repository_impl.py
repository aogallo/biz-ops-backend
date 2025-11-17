from typing import override

from sqlmodel import Session, select

from app.domain.entities.product import Product, ProductCreate
from app.domain.repositories.product_respository import ProductRepository
from app.infrastructure.database import get_current_session


class ProductRepositoryImpl(ProductRepository):
    """Implementation of ProductRepository interface."""

    def __init__(self, session: Session | None = None) -> None:
        # Use provided session or get from context
        self.db = session or get_current_session()

    @override
    def create(self, product: ProductCreate) -> Product:
        db_product = Product.model_validate(product)
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    @override
    def get_by_name(self, name: str) -> Product | None:
        statement = select(Product).where(Product.name == name)
        return self.db.exec(statement=statement).one_or_none()

    @override
    def get_by_id(self, product_id: int) -> Product | None:

        return self.db.get(Product, product_id)

    @override
    def delete(self, product_id: int) -> bool:
        db_product = self.db.get(Product, product_id)
        if db_product is None:
            return False

        self.db.delete(db_product)
        return True

    @override
    def get_all(self) -> list[Product]:
        return list(self.db.exec(select(Product)))

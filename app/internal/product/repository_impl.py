from typing import override
from uuid import UUID

from sqlmodel import Session, func, select

from app.internal.product.entity import Product, ProductCreate
from app.internal.product.respository import ProductRepository
from app.internal.user.entity import User


class ProductRepositoryImpl(ProductRepository):
    """
    Implementation of Product Repository.
    All queries are automatically scoped to organization_id for multi-tenancy.
    Products are organization-scoped (shared across companies).
    """

    def __init__(
        self, session: Session, current_user: User, organization_id: UUID
    ) -> None:
        self.db = session
        self.current_user = current_user
        self.organization_id = (
            organization_id  # Organization context for multi-tenancy
        )

    @override
    def create(self, product: ProductCreate) -> Product:
        """Create a new product scoped to this organization"""
        db_product: Product = Product.model_validate(
            product,
            update={
                "organization_id": self.organization_id,
                "created_by": self.current_user.auth0_user_id,
            },
        )
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    @override
    def get_by_name(self, name: str) -> Product | None:
        """Get a product by name (scoped to organization)"""
        statement = select(Product).where(
            Product.organization_id == self.organization_id,
            Product.name == name,
        )
        product: Product | None = self.db.exec(
            statement=statement
        ).one_or_none()
        return product

    @override
    def get_by_id(self, product_id: UUID) -> Product | None:
        """Get a product by id (scoped to organization)"""
        statement = select(Product).where(
            Product.organization_id == self.organization_id,
            Product.id == product_id,
        )
        product: Product | None = self.db.exec(statement).one_or_none()
        return product

    @override
    def delete(self, product_id: UUID) -> bool:
        """Delete a product by id (scoped to organization)"""
        product: Product | None = self.get_by_id(product_id)
        if product is None:
            return False
        self.db.delete(product)
        self.db.commit()
        return True

    @override
    def get_all(self, offset: int, limit: int) -> list[Product]:
        """Get all products (scoped to organization)"""
        products: list[Product] = list(
            self.db.exec(
                select(Product)
                .where(Product.organization_id == self.organization_id)
                .offset(offset)
                .limit(limit)
            )
        )
        return products

    def get_count(self) -> int:
        """Get count of products (scoped to organization)"""
        count_statement = (
            select(func.count())
            .select_from(Product)
            .where(Product.organization_id == self.organization_id)
        )
        count: int = self.db.exec(count_statement).one()
        return count

from abc import ABC, abstractmethod
from uuid import UUID

from app.internal.product.entity import Product, ProductCreate


class ProductRepository(ABC):
    """Product repository interface"""

    @abstractmethod
    def create(self, product: ProductCreate) -> Product:
        """Create a new product"""
        pass

    @abstractmethod
    def get_by_name(self, name: str) -> Product | None:
        """Get a product by name"""
        pass

    @abstractmethod
    def get_by_id(self, product_id: UUID) -> Product | None:
        """Get a product by id"""
        pass

    @abstractmethod
    def delete(self, product_id: UUID) -> bool:
        """Delete a product by id"""
        pass

    @abstractmethod
    def get_all(self, offset: int, limit: int) -> list[Product]:
        """Get all products"""
        pass

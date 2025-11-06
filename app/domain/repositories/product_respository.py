from abc import ABC, abstractmethod

from app.domain.entities.product import Product, ProductCreate


class ProductRepository(ABC):
    @abstractmethod
    def create(self, product: ProductCreate) -> Product:
        """Create a new product using Product Create schema"""
        pass

    @abstractmethod
    def get_by_name(self, name: str) -> Product | None:
        """Get a product using name"""
        pass

    @abstractmethod
    def get_by_id(self, product_id: int) -> Product | None:
        """Get a product using id"""
        pass

    @abstractmethod
    def delete(self, product_id: int) -> bool:
        """Delete a product using id"""
        pass

    @abstractmethod
    def get_all(self) -> list[Product]:
        """Get a list of products"""
        pass

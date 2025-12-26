from abc import ABC, abstractmethod
from uuid import UUID

from app.internal.category.entity import Category, CategoryCreate


class CategoryRepository(ABC):
    """
    Category repository (organization-scoped).
    """

    @abstractmethod
    def create(self, category: CategoryCreate) -> Category:
        """
        Create a category
        """
        pass

    @abstractmethod
    def get_all(self, offset: int, limit: int) -> list[Category]:
        """
        Get all categories (scoped to organization)
        """
        pass

    @abstractmethod
    def get_by_id(self, category_id: UUID) -> Category | None:
        """
        Get a category by id (scoped to organization)
        """
        pass

    @abstractmethod
    def get_by_name(self, name: str) -> Category | None:
        """
        Get a category by name (scoped to organization)
        """
        pass

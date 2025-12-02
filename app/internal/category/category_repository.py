from abc import ABC, abstractmethod

from app.internal.category.category_entity import Category, CategoryCreate


class CategoryRepository(ABC):
    """
    Category repository
    """

    @abstractmethod
    def create(self, category: CategoryCreate) -> Category:
        """
        Create a company
        """
        pass

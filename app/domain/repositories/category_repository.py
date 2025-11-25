from abc import ABC, abstractmethod

from app.domain.entities.category import Category, CategoryCreate


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

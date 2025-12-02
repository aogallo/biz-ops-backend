from sqlmodel import Session

from app.domain.entities.category import Category, CategoryCreate
from app.domain.repositories.category_repository import CategoryRepository


class CategoryRepositoryImpl(CategoryRepository):
    """Implementation of Category Repository"""

    def __init__(self, session: Session) -> None:
        self.db = session

    def create(self, category: CategoryCreate) -> Category:
        new_category: Category = Category.model_validate(category)
        self.db.add(new_category)
        self.db.commit()
        self.db.refresh(new_category)
        return new_category

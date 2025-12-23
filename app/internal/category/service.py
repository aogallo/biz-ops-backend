from sqlmodel import Session

from app.internal.category.entity import CategoryCreate
from app.internal.category.repository_impl import CategoryRepositoryImpl


class CategoryService:
    """Service for managing categories."""

    def __init__(self, session: Session) -> None:
        self._category_repo = CategoryRepositoryImpl(session)

    def create_category(self, category: CategoryCreate):
        return self._category_repo.create(category)

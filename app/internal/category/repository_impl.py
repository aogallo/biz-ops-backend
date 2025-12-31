from uuid import UUID

from sqlmodel import Session, func, select

from app.internal.category.entity import Category, CategoryCreate
from app.internal.category.repository import CategoryRepository
from app.internal.user.entity import User


class CategoryRepositoryImpl(CategoryRepository):
    """
    Implementation of Category Repository.
    All queries are automatically scoped to organization_id for multi-tenancy.
    Categories are organization-scoped (shared across companies).
    """

    def __init__(
        self, session: Session, current_user: User, organization_id: UUID
    ) -> None:
        self.db = session
        self.current_user = current_user
        self.organization_id = (
            organization_id  # Organization context for multi-tenancy
        )

    def create(self, category: CategoryCreate) -> Category:
        """Create a new category scoped to this organization"""
        new_category: Category = Category.model_validate(
            category,
            update={
                "organization_id": self.organization_id,
                "created_by": self.current_user.auth0_user_id,
            },
        )
        self.db.add(new_category)
        self.db.commit()
        self.db.refresh(new_category)
        return new_category

    def get_all(self, offset: int, limit: int) -> list[Category]:
        """Get all categories (scoped to organization)"""
        statement = (
            select(Category)
            .where(Category.organization_id == self.organization_id)
            .offset(offset)
            .limit(limit)
        )
        categories: list[Category] = list(self.db.exec(statement))
        return categories

    def get_by_id(self, category_id: UUID) -> Category | None:
        """Get a category by id (scoped to organization)"""
        statement = select(Category).where(
            Category.organization_id == self.organization_id,
            Category.id == category_id,
        )
        category: Category | None = self.db.exec(statement).one_or_none()
        return category

    def get_by_name(self, name: str) -> Category | None:
        """Get a category by name (scoped to organization)"""
        statement = select(Category).where(
            Category.organization_id == self.organization_id,
            Category.name == name,
        )
        category: Category | None = self.db.exec(statement).one_or_none()
        return category

    def get_count(self) -> int:
        """Get count of categories (scoped to organization)"""
        count_statement = (
            select(func.count())
            .select_from(Category)
            .where(Category.organization_id == self.organization_id)
        )
        count: int = self.db.exec(count_statement).one()
        return count

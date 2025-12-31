from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import Session

from app.internal.category.entity import CategoryCreate
from app.internal.category.repository_impl import CategoryRepositoryImpl
from app.internal.user.entity import User


class CategoryService:
    """Service for managing categories (organization-scoped)."""

    def __init__(
        self,
        session: Session,
        current_user: User,
        organization_id: UUID | None = None,
    ) -> None:
        # Use provided organization_id or extract from current_user
        org_id = organization_id or current_user.organization_id
        if not org_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must belong to an organization",
            )
        self._category_repo = CategoryRepositoryImpl(
            session, current_user, org_id
        )

    def create_category(self, category: CategoryCreate):
        return self._category_repo.create(category)

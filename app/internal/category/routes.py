from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.dependencies import get_current_user, verify_token
from app.internal.category.entity import CategoryCreate
from app.internal.category.service import CategoryService

router = APIRouter(
    prefix="/category",
    tags=["Category"],
    dependencies=[Depends(verify_token)],
)


@router.post("")
def create_category(
    category: CategoryCreate,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """Create a new category (organization-scoped)."""
    service = CategoryService(session, current_user)
    return service.create_category(category)

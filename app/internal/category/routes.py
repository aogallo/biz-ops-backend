from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.dependencies import verify_token
from app.infrastructure.database import get_session
from app.internal.category.entity import CategoryCreate
from app.internal.category.service import CategoryService

router = APIRouter(
    prefix="/category",
    tags=["category"],
    dependencies=[Depends(verify_token)],
)


@router.post("")
def create_category(
    category: CategoryCreate, session: Session = Depends(get_session)
):
    service = CategoryService(session)
    return service.create_category(category)

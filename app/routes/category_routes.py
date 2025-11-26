from fastapi import APIRouter, Depends

from app.dependencies import verify_token
from app.domain.entities.category import CategoryCreate
from app.infrastructure.database import get_session
from app.services.category_service import CategoryService

router = APIRouter(
    prefix="/category",
    tags=["category"],
    dependencies=[Depends(verify_token), Depends(get_session)],
)


@router.post("")
def create_category(category: CategoryCreate):
    service = CategoryService()
    return service.create_category(category)

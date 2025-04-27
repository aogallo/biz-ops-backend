from fastapi import APIRouter, Depends

from app.services.user_service import UserService
from app.dependencies import verify_token
from app.infrastructure.database import get_session
from app.infrastructure.repositories.user_repository_impl import UserRepositoryImpl


router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[
        Depends(get_session),
        Depends(verify_token),
    ],
)


@router.get("/")
def read_users():
    user_repo = UserRepositoryImpl()
    user_service = UserService(user_repo)
    return user_service.list_users()

from fastapi import APIRouter, Depends

from app.services.user_service import UserService
from app.dependencies import verify_token
from app.infrastructure.database import SessionDep
from app.infrastructure.repositories.user_repository_impl import UserRepositoryImpl


router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[],
)


@router.get("/")
def read_users(
    current_user=Depends(verify_token()),
    session=SessionDep,
):
    user_repo = UserRepositoryImpl(session, current_user)
    user_service = UserService(user_repo)
    return user_service.list_users()

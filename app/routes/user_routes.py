from typing import Annotated
from fastapi import APIRouter, Depends

from app.services.user_service import UserService
from app.dependencies import get_current_user
from app.infrastructure.database import SessionDep
from app.infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from app.domain.entities.user import User


router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[],
)


@router.get("/")
def read_users(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    user_repo = UserRepositoryImpl(db=session, current_user=current_user)
    user_service = UserService(user_repo)
    return user_service.list_users()

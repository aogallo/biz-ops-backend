from fastapi import APIRouter, Depends

from app.services.user_service import UserService
from app.dependencies import verify_token
from app.infrastructure.database import get_session
from app.infrastructure.repositories.user_repository_impl import UserRepositoryImpl, get_user_repository
from app.schemas.user_schema import UserListResponse, UserResponse


router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[
        Depends(verify_token),
        Depends(get_session),  # This ensures a session is available in the context
    ],
)


@router.get("/", response_model=list[UserResponse])
def read_users(user_repo: UserRepositoryImpl = Depends(get_user_repository)):
    """
    Get all users.
    
    Returns a list of all users in the system.
    Requires authentication.
    """
    user_service = UserService(user_repo)
    users = user_service.list_users()
    return users

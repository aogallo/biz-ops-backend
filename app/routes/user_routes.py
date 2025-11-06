from fastapi import APIRouter, Depends

from app.dependencies import verify_token
from app.infrastructure.database import get_session
from app.schemas.user_schema import UserResponse
from app.services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[
        Depends(verify_token),
        Depends(
            get_session
        ),  # This ensures a session is available in the context
    ],
)


@router.get("/", response_model=list[UserResponse])
def read_users():
    """
    Get all users.

    Returns a list of all users in the system.
    Requires authentication.
    """
    user_service = UserService()
    users = user_service.list_users()
    return users

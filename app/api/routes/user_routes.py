from fastapi import APIRouter, Depends

from app.application.services.user_service import UserService
from app.dependencies import verify_token
from app.infrastructure.database import SessionDep


router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(verify_token), Depends(SessionDep)],
)


@router.get("/")
async def read_users():
    pass

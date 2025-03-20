from typing import Annotated
from fastapi import APIRouter, Depends
from app.services.auth_service import AuthService

from app.dependencies import oauth2_scheme


router = APIRouter()


@router.get("/login")
async def login(
    token: Annotated[str, Depends(oauth2_scheme)],
):
    print(f"Token from hte route: {token}")
    auth_service = AuthService()
    data = auth_service.login(token)

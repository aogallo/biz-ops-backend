"""
Development-only authentication routes.
These endpoints are only available when USE_MOCK_AUTH=True.
"""

import logging
from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr

from app.core.config import settings
from app.dependencies import get_current_user
from app.domain.entities.user import User
from app.infrastructure.database import SessionDep
from app.infrastructure.repositories.user_repository_impl import (
    UserRepositoryImpl,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dev", tags=["Development"])


class DevTokenRequest(BaseModel):
    """Request model for generating dev tokens."""

    auth_id: str = "dev_user"
    email: EmailStr = "dev@example.com"
    picture: str | None = None


class DevTokenResponse(BaseModel):
    """Response model for dev token endpoint."""

    access_token: str
    token_type: str
    user: dict


class WhoAmIResponse(BaseModel):
    """Response model for whoami endpoint."""

    auth_id: str
    email: str
    picture: str | None
    created_at: datetime
    mock_mode: bool


def check_dev_mode():
    """
    Dependency to ensure endpoint only works in development mode.
    """
    if not settings.USE_MOCK_AUTH:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endpoint not available in production mode",
        )


@router.post("/token", response_model=DevTokenResponse)
async def get_dev_token(
    request: DevTokenRequest,
    session: SessionDep,
    _: None = Depends(check_dev_mode),
):
    """
    Generate a mock JWT token for development/testing.

    This endpoint only works when USE_MOCK_AUTH=True.
    It creates or retrieves a test user and generates a mock JWT token.

    Example request:
    ```
    POST /dev/token
    {
        "auth_id": "dev_user",
        "email": "dev@example.com"
    }
    ```

    Example response:
    ```
    {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "token_type": "Bearer",
        "user": {
            "auth_id": "dev_user",
            "email": "dev@example.com"
        }
    }
    ```

    Usage in Postman/curl:
    - Copy the access_token value
    - Add header: Authorization: Bearer <access_token>
    """
    logger.info(
        "Generating dev token for user: %s (email: %s)",
        request.auth_id,
        request.email,
    )

    # Get or create the user in the database
    user_repo = UserRepositoryImpl(session)
    user = user_repo.get_user_by_id(request.auth_id)

    if not user:
        logger.info("Creating new dev user: %s", request.auth_id)
        user = User(
            auth_id=request.auth_id,
            email=request.email,
            picture=request.picture or "https://via.placeholder.com/150",
            created_by="system",
            created_at=datetime.now(UTC),
        )
        user = user_repo.create_user(user)
    else:
        logger.info("Found existing dev user: %s", request.auth_id)

    # Generate mock JWT token
    # In mock mode, we don't need a real signature since verify_token skips validation
    payload = {
        "sub": user.auth_id,
        "email": user.email,
        "picture": user.picture,
        "iat": datetime.now(UTC),
        "exp": datetime.now(UTC) + timedelta(days=7),  # 7 days expiry
        "aud": settings.AUTH0_AUDIENCE or "dev-api",
        "iss": settings.AUTH0_ISSUER or "dev-issuer",
    }

    # Create token without signature (since we're in dev mode)
    token = jwt.encode(payload, "dev-secret-key", algorithm="HS256")

    logger.info("Successfully generated dev token for user: %s", user.auth_id)

    return {
        "access_token": token,
        "token_type": "Bearer",
        "user": {
            "auth_id": user.auth_id,
            "email": user.email,
            "picture": user.picture,
        },
    }


@router.get("/whoami", response_model=WhoAmIResponse)
async def whoami(
    current_user: Annotated[User, Depends(get_current_user)],
    _: None = Depends(check_dev_mode),
):
    """
    Get information about the currently authenticated user.

    This endpoint helps verify that authentication is working correctly.
    It requires a valid token in the Authorization header.

    Example:
    ```
    GET /dev/whoami
    Authorization: Bearer <your-token>
    ```
    """
    logger.info("Whoami request for user: %s", current_user.auth_id)

    return {
        "auth_id": current_user.auth_id,
        "email": current_user.email,
        "picture": current_user.picture,
        "created_at": current_user.created_at,
        "mock_mode": settings.USE_MOCK_AUTH,
    }

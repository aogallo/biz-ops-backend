"""JWT Authentication backend for fastapi-users."""

from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)

from app.core.config import settings

# Bearer token transport (Authorization: Bearer <token>)
bearer_transport = BearerTransport(tokenUrl="auth/login")


def get_jwt_strategy() -> JWTStrategy:
    """
    Create JWT strategy for authentication.

    Returns:
        JWTStrategy configured with app settings
    """
    return JWTStrategy(
        secret=settings.JWT_SECRET,
        lifetime_seconds=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        algorithm=settings.JWT_ALGORITHM,
    )


# Authentication backend combining transport and strategy
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

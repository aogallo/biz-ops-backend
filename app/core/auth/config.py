"""FastAPI Users configuration and setup."""

from fastapi_users import FastAPIUsers
from uuid import UUID

from app.core.auth.backend import auth_backend
from app.core.auth.manager import get_user_manager
from app.internal.user.entity import User

# FastAPIUsers instance - provides authentication routes and dependencies
fastapi_users = FastAPIUsers[User, UUID](
    get_user_manager,
    [auth_backend],
)

# Dependency to get current active user
current_active_user = fastapi_users.current_user(active=True)

# Dependency to get current active verified user
current_active_verified_user = fastapi_users.current_user(
    active=True, verified=True
)

# Dependency to get current superuser
current_superuser = fastapi_users.current_user(active=True, superuser=True)

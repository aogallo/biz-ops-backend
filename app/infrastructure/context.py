from fastapi import Depends
from app.domain.entities.user import User
from app.dependencies import get_current_user
from app.infrastructure.database import user_context


def set_user_context(current_user: User = Depends(get_current_user)):
    token = user_context.set(current_user)
    try:
        yield current_user
    finally:
        user_context.reset(token) 
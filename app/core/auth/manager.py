"""User manager for handling user operations."""

from typing import Optional
from uuid import UUID

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, UUIDIDMixin
from sqlmodel import Session

from app.core.config import settings
from app.database import get_session
from app.internal.user.entity import User


class UserManager(UUIDIDMixin, BaseUserManager[User, UUID]):
    """
    User manager for handling user lifecycle events.

    Extends fastapi-users BaseUserManager to add custom behavior
    for user registration, password reset, email verification, etc.
    """

    reset_password_token_secret = settings.JWT_SECRET
    verification_token_secret = settings.JWT_SECRET

    async def on_after_register(
        self, user: User, request: Optional[Request] = None
    ):
        """
        Called after a user successfully registers.

        Args:
            user: The newly registered user
            request: The request object
        """
        print(f"User {user.id} ({user.email}) has registered.")
        # TODO: Send welcome email in Phase 1
        # await send_welcome_email(user.email, user.first_name)

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """
        Called after a user requests a password reset.

        Args:
            user: The user requesting password reset
            token: The password reset token
            request: The request object
        """
        print(
            f"User {user.id} ({user.email}) has forgotten their password. "
            f"Reset token: {token}"
        )
        # TODO: Send password reset email in Phase 1
        # reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        # await send_password_reset_email(user.email, reset_url)

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """
        Called after a user requests email verification.

        Args:
            user: The user requesting verification
            token: The verification token
            request: The request object
        """
        print(
            f"Verification requested for user {user.id} ({user.email}). "
            f"Verification token: {token}"
        )
        # TODO: Send verification email in Phase 1
        # verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        # await send_verification_email(user.email, verify_url)

    async def on_after_verify(
        self, user: User, request: Optional[Request] = None
    ):
        """
        Called after a user successfully verifies their email.

        Args:
            user: The user who verified their email
            request: The request object
        """
        print(f"User {user.id} ({user.email}) has been verified.")


async def get_user_manager(
    session: Session = Depends(get_session),
) -> UserManager:
    """
    Dependency to get UserManager instance.

    Args:
        session: Database session

    Yields:
        UserManager instance
    """
    yield UserManager(session)

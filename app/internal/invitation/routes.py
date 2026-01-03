"""Invitation management API routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.database import get_session
from app.dependencies import get_current_user
from app.internal.invitation.schema import (
    InvitationAcceptRequest,
    InvitationAcceptResponse,
    InvitationCreate,
    InvitationListResponse,
    InvitationResponse,
    InvitationVerifyResponse,
)
from app.internal.invitation.service import InvitationService
from app.internal.user.entity import User

router = APIRouter()


@router.post(
    "/invitations",
    response_model=InvitationResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Invitations"],
)
def create_invitation(
    invitation_data: InvitationCreate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Create a new invitation.

    Only super admins can send invitations.
    Automatically generates a secure token and sets 7-day expiration.
    """
    service = InvitationService(session, current_user)
    invitation = service.create_invitation(
        email=invitation_data.email,
        organization_id=invitation_data.organization_id,
        default_role=invitation_data.default_role,
        company_ids=invitation_data.company_ids,
    )
    return invitation


@router.get(
    "/invitations",
    response_model=InvitationListResponse,
    tags=["Invitations"],
)
def list_invitations(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    organization_id: UUID,
    status: str | None = None,
):
    """
    List all invitations for an organization.

    Optionally filter by status: pending, accepted, expired, revoked
    """
    from app.internal.invitation.entity import InvitationStatus

    status_filter = InvitationStatus(status) if status else None
    service = InvitationService(session, current_user)
    invitations = service.list_invitations(
        organization_id=organization_id, status=status_filter
    )
    return InvitationListResponse(
        invitations=invitations, total=len(invitations)
    )


@router.get(
    "/invitations/{token}/verify",
    response_model=InvitationVerifyResponse,
    tags=["Invitations"],
)
def verify_invitation_token(
    token: str,
    session: Annotated[Session, Depends(get_session)],
):
    """
    Verify invitation token validity.

    Public endpoint - no authentication required.
    Returns token status and invitation details.
    """
    # Create a temporary user for unauthenticated access
    from app.internal.user.entity import User as TempUser

    temp_user = TempUser(
        email="system@temp.com",
        hashed_password="",
        is_active=True,
        is_superuser=False,
        is_verified=False,
        auth_id="temp",
        auth0_user_id="temp",
    )

    service = InvitationService(session, temp_user)
    result = service.verify_token(token)
    return result


@router.post(
    "/invitations/{token}/accept",
    response_model=InvitationAcceptResponse,
    tags=["Invitations"],
)
def accept_invitation(
    token: str,
    accept_data: InvitationAcceptRequest,
    session: Annotated[Session, Depends(get_session)],
):
    """
    Accept an invitation and create user account.

    Public endpoint - no authentication required.
    Creates user account and returns access token for immediate login.

    Body should include either:
    - password (for email/password auth)
    - oauthProvider + oauthCode (for OAuth auth)
    """
    # Create a temporary user for unauthenticated access
    from app.internal.user.entity import User as TempUser

    temp_user = TempUser(
        email="system@temp.com",
        hashed_password="",
        is_active=True,
        is_superuser=False,
        is_verified=False,
        auth_id="temp",
        auth0_user_id="temp",
    )

    service = InvitationService(session, temp_user)
    result = service.accept_invitation(
        token=token,
        password=accept_data.password,
        oauth_provider=accept_data.oauth_provider,
        oauth_code=accept_data.oauth_code,
    )
    return result


@router.delete(
    "/invitations/{invitation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Invitations"],
)
def delete_invitation(
    invitation_id: UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Delete an invitation.

    Requires: Super admin access
    """
    service = InvitationService(session, current_user)
    service.delete_invitation(invitation_id)

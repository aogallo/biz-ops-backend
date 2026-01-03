"""Business logic for invitation management."""

import asyncio
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.core.email import send_welcome_email
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    validate_password,
)
from app.internal.invitation.entity import Invitation, InvitationStatus
from app.internal.invitation.repository_impl import InvitationRepositoryImpl
from app.internal.user.entity import User, UserCompanyAccess


class InvitationService:
    """Service for invitation business logic."""

    def __init__(self, session: Session, current_user: User):
        """Initialize service with database session and current user.

        Args:
            session: Database session
            current_user: Current authenticated user
        """
        self.repository = InvitationRepositoryImpl(session, current_user)
        self.current_user = current_user

    def create_invitation(
        self,
        email: str,
        organization_id: UUID,
        default_role: str | None = None,
        company_ids: list[UUID] | None = None,
    ) -> Invitation:
        """Create a new invitation.

        Args:
            email: Invitee email address
            organization_id: Organization ID
            default_role: Default role to assign
            company_ids: Optional list of company IDs for access

        Returns:
            Created invitation

        Raises:
            HTTPException: 400 if validation fails
        """
        # Generate secure token (256-bit)
        token = secrets.token_urlsafe(32)

        # Set expiration (7 days from now)
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)

        # Revoke any pending invitations for this email in this organization
        self.repository.revoke_pending_invitations(email, organization_id)

        # Create new invitation
        return self.repository.create_invitation(
            email=email,
            organization_id=organization_id,
            token=token,
            invited_by=self.current_user.id,
            expires_at=expires_at,
            default_role=default_role,
            company_ids=company_ids,
        )

    def list_invitations(
        self,
        organization_id: UUID,
        status: InvitationStatus | None = None,
    ) -> list[Invitation]:
        """List invitations for an organization.

        Args:
            organization_id: Organization ID
            status: Optional status filter

        Returns:
            List of invitations
        """
        return self.repository.get_all_by_organization(
            organization_id=organization_id, status=status
        )

    def get_invitation_by_id(self, invitation_id: UUID) -> Invitation:
        """Get invitation by ID.

        Args:
            invitation_id: Invitation ID

        Returns:
            Invitation

        Raises:
            HTTPException: 404 if not found
        """
        invitation = self.repository.get_by_id(invitation_id)
        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Invitation with ID '{invitation_id}' not found",
            )
        return invitation

    def verify_token(self, token: str) -> dict:
        """Verify invitation token.

        Args:
            token: Invitation token

        Returns:
            Dict with verification result
        """
        invitation = self.repository.get_by_token(token)

        if not invitation:
            return {
                "valid": False,
                "message": "Invalid invitation token",
            }

        # Check if already used
        if invitation.status != InvitationStatus.PENDING:
            return {
                "valid": False,
                "message": f"Invitation already {invitation.status.value}",
            }

        # Check if expired
        if datetime.now(timezone.utc) > invitation.expires_at:
            # Mark as expired
            self.repository.update_status(
                invitation.id, InvitationStatus.EXPIRED
            )
            return {
                "valid": False,
                "message": "Invitation has expired",
            }

        return {
            "valid": True,
            "email": invitation.email,
            "organization_id": str(invitation.organization_id),
            "expires_at": invitation.expires_at.isoformat(),
        }

    def accept_invitation(
        self,
        token: str,
        password: str | None = None,
        oauth_provider: str | None = None,
        oauth_code: str | None = None,
    ) -> dict:
        """Accept an invitation and create user account.

        Args:
            token: Invitation token
            password: Password for email/password auth
            oauth_provider: OAuth provider ("google" or "github")
            oauth_code: OAuth authorization code

        Returns:
            Dict with access token and user data

        Raises:
            HTTPException: 400/404 if validation fails
        """
        # Verify token first
        verification = self.verify_token(token)
        if not verification["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=verification["message"],
            )

        invitation = self.repository.get_by_token(token)
        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found",
            )

        # Get database session from repository
        session = self.repository.db

        # Check if user already exists with this email
        statement = select(User).where(User.email == invitation.email)
        existing_user = session.exec(statement).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with email '{invitation.email}' already exists",
            )

        # Validate authentication method
        if not password and not (oauth_provider and oauth_code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either password or OAuth credentials must be provided",
            )

        # Create user account
        user_id = uuid4()
        hashed_pwd = None

        if password:
            # Email/password authentication
            is_valid, error_message = validate_password(password)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_message,
                )
            hashed_pwd = hash_password(password)

        # Create user
        user = User(
            id=user_id,
            email=invitation.email,
            hashed_password=hashed_pwd,
            organization_id=invitation.organization_id,
            is_active=True,
            is_verified=True,  # Auto-verify invited users
            is_superuser=False,
            # Temporary Auth0 fields (will be removed in Phase 7)
            auth_id=f"local|{user_id}",
            auth0_user_id=f"invitation|{user_id}",
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        # Create UserCompanyAccess entries if company_ids provided
        if invitation.company_ids:
            from datetime import datetime

            for company_id_str in invitation.company_ids:
                company_id = UUID(company_id_str)
                access = UserCompanyAccess(
                    user_id=user.id,
                    company_id=company_id,
                    role=invitation.default_role or "viewer",
                    created_by=str(self.current_user.id),
                    created_at=datetime.utcnow(),
                )
                session.add(access)

            session.commit()

        # Mark invitation as accepted
        invitation.status = InvitationStatus.ACCEPTED
        invitation.accepted_at = datetime.now(timezone.utc)
        invitation.accepted_by = user.id
        session.add(invitation)
        session.commit()

        # Generate access and refresh tokens
        token_data = {"sub": str(user.id)}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        # Send welcome email (async, don't wait)
        asyncio.create_task(
            send_welcome_email(
                to_email=user.email,
                first_name=user.first_name,
            )
        )

        # Return token and user data
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "firstName": user.first_name,
                "lastName": user.last_name,
                "organizationId": str(user.organization_id)
                if user.organization_id
                else None,
                "isActive": user.is_active,
                "isVerified": user.is_verified,
                "isSuperuser": user.is_superuser,
            },
        }

    def delete_invitation(self, invitation_id: UUID) -> None:
        """Delete an invitation.

        Args:
            invitation_id: Invitation ID

        Raises:
            HTTPException: 404 if not found
        """
        invitation = self.repository.get_by_id(invitation_id)
        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Invitation with ID '{invitation_id}' not found",
            )

        self.repository.delete_invitation(invitation_id)
